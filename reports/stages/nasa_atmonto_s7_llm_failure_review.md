# NASA ATMONTO S7 LLM Failure Review

Date: 2026-06-03

Status: manual review of the bounded 24-case S7 LLM answer-generation check.
This is a diagnostic review, not human certification of answer quality.

## Scope

Reviewed artifact:
`reports/stages/nasa_atmonto_s7_llm_answer_generation.json`

The reviewed run uses prompt version `nasa_atmonto_s7_llm_answer_v2`, with
12 selected cases per routed mode and two selected cases per CQ template.

Aggregate result:

| Mode | Selected | Correctness | Citation precision | Citation recall | Evidence faithful | Unsupported claim rate | Abstention correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 12 | 1.0 | 1.0 | 0.6111 | 1.0 | 0.0 | 1.0 |
| `routed_token_matched_dense_graphrag` | 12 | 0.5 | 1.0 | 0.6111 | 0.5 | 0.3333 | 0.5 |

## Failure Taxonomy

| Category | Cases | Affected templates | Root cause | Claim impact | Recommended action |
| --- | ---: | --- | --- | --- | --- |
| Dense source miss on source-local temporal CQs | 2 | `QT-Q01-TIME-WINDOW` | Dense retrieval selected the wrong advisory metadata chunk, so the LLM correctly abstained from insufficient evidence but failed the source-bounded answer task. | This is a dense retrieval failure, not an ontology or time-normalization failure. | Add source-id/date metadata filtering or source-family lexical prefiltering before dense retrieval for source-local CQs. |
| Wrong-context abstention under source-bounded scoring | 2 | `QT-A01-ABSTENTION-FIELDS` | Dense retrieval selected an unrelated metadata/header chunk. The LLM abstained, but the scorer marks this incorrect because target-source retrieval is required for live retrieval modes. | The abstention policy is intentionally strict; otherwise any wrong-context abstention could appear correct. | Keep the strict target-source guard; improve dense retrieval before treating abstention accuracy as meaningful. |
| Compound CQ partial-answer ambiguity | 2 | `QT-Q01-ROUTE-SEMANTICS` | The retrieved target source and graph triple support `controlledNASelement=BNA`, but the LLM abstained because reroute type/reason were unsupported. | This is a CQ/prompt granularity issue, not a source retrieval miss. | Split route-semantics CQs into separately scored fields, or add a controlled partial-answer policy and evaluate it as a separate ablation. |

## Reviewed Failure Cards

### F1. Time Window Dense Miss: `2026-05-19:032`

- Template: `QT-Q01-TIME-WINDOW`
- Expected values:
  `effectiveStartTime=2026-05-19T13:22:00Z`,
  `effectiveEndTime=2026-05-19T16:30:00Z`
- Dense routed context:
  `atcscc-2026-05-19-144-p1-c1`, source `2026-05-19:144`
- LLM behavior: abstained because the supplied evidence did not contain a time
  range.
- Live lexical comparison: retrieved `atcscc-2026-05-19-032-p1-c1` containing
  `EFFECTIVE TIME: 191322-191630`, normalized to the expected ISO values.

Assessment: dense retrieval missed the target advisory.

### F2. Time Window Dense Miss: `2026-05-15:063`

- Template: `QT-Q01-TIME-WINDOW`
- Expected values:
  `effectiveStartTime=2026-05-15T19:18:00Z`,
  `effectiveEndTime=2026-05-16T00:30:00Z`
- Dense routed context:
  `atcscc-2026-05-19-144-p1-c1`, source `2026-05-19:144`
- LLM behavior: abstained because the supplied evidence did not contain a time
  range.
- Live lexical comparison: retrieved `atcscc-2026-05-15-063-p1-c1` containing
  `EFFECTIVE TIME: 151918-160030`, normalized to the expected ISO values.

Assessment: dense retrieval missed the target advisory.

### F3. Route Semantics Partial Answer: `2026-05-19:079`

- Template: `QT-Q01-ROUTE-SEMANTICS`
- Expected value: `controlledNASelement=BNA`
- Dense routed context:
  `atcscc-2026-05-19-079-p1-c1`, text `CTL ELEMENT: BNA`
- Graph triple: `t1`, predicate `controlledNASelement`, object `BNA`
- LLM behavior: abstained because reroute type and reroute reason were not
  supported, even though the controlled NAS element was supported.
- Live lexical comparison: returned the supported `controlledNASelement=BNA`
  value and noted the unsupported route fields.

Assessment: this is a partial-answer policy mismatch for a compound CQ. The
retrieval context was sufficient for the scored field.

### F4. Route Semantics Partial Answer: `2026-05-19:074`

- Template: `QT-Q01-ROUTE-SEMANTICS`
- Expected value: `controlledNASelement=BNA`
- Dense routed context:
  `atcscc-2026-05-19-074-p1-c1`, text `CTL ELEMENT: BNA`
- Graph triple: `t1`, predicate `controlledNASelement`, object `BNA`
- LLM behavior: abstained because reroute type and reroute reason were not
  supported.
- Live lexical comparison: returned the supported `controlledNASelement=BNA`
  value and noted unsupported route fields.

Assessment: this is the same compound-CQ partial-answer issue as F3.

### F5. Abstention Dense Miss: `2026-05-19:032`

- Template: `QT-A01-ABSTENTION-FIELDS`
- Expected behavior: abstain on unsupported expected fields, but only after
  retrieving the target advisory source context.
- Dense routed context:
  `atcscc-2026-05-18-021-p1-c1`, source `2026-05-18:021`
- LLM behavior: abstained from unrelated metadata/header evidence.
- Scoring behavior: incorrect, because live/dense retrieval modes must retrieve
  the target source before abstention can count as correct.

Assessment: wrong-context abstention should remain a failure.

### F6. Abstention Dense Miss: `2026-05-15:063`

- Template: `QT-A01-ABSTENTION-FIELDS`
- Expected behavior: abstain on unsupported expected fields, but only after
  retrieving the target advisory source context.
- Dense routed context:
  `atcscc-2026-05-18-021-p1-c1`, source `2026-05-18:021`
- LLM behavior: abstained from unrelated metadata/header evidence.
- Scoring behavior: incorrect, because live/dense retrieval modes must retrieve
  the target source before abstention can count as correct.

Assessment: wrong-context abstention should remain a failure.

## Implications for SOTA Story

1. The 24-case LLM check supports the current claim that live lexical routed
   context is stronger than dense retrieval for source-bounded ATCSCC advisory
   questions.
2. The dense result should be framed as a negative retrieval result under the
   current source-bounded setup, not as evidence that dense retrieval is
   generally weak.
3. The route-semantics failures show that compound CQs need either finer field
   decomposition or an explicit partial-answer policy. This is a methodology
   refinement, not evidence that graph context is unavailable.
4. The abstention failures validate the strict source-bounded scoring rule:
   abstention is only correct when the target source context was actually
   retrieved.

## Next Engineering Step

Prioritize a deterministic dense-retrieval guard before increasing LLM sample
size:

1. Add source-family/date/advisory-number metadata filtering for dense retrieval
   when the CQ is source-local or the question includes a source identifier.
2. Split `QT-Q01-ROUTE-SEMANTICS` into separately scored fields, or add a
   controlled partial-answer ablation with explicit expected semantics.
3. Rerun the 24-case S7 LLM check only after the retrieval and CQ-contract
   changes are explicit.
