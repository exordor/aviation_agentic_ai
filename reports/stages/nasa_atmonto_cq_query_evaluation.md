# NASA ATMONTO CQ Query and Answer-Quality Evaluation

## Scope

- Gold set: `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- Boundary: Deterministic answer-set evaluation only; LLM answer generation is not run.
- GraphRAG layer: pre_generation_answer_set_quality
- LLM generation: `not_run`

## Aggregate by System

| System | Gold answers | Predicted | TP | FP | FN | Micro P | Micro R | Micro F1 | Macro F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `S0_rule_only` | 697 | 636 | 502 | 134 | 195 | 0.7893 | 0.7202 | 0.7532 | 0.6689 |
| `S2_llm_schema_slice` | 697 | 792 | 421 | 371 | 276 | 0.5316 | 0.604 | 0.5655 | 0.5517 |
| `S3_llm_schema_slice_validator_repair` | 697 | 517 | 327 | 190 | 370 | 0.6325 | 0.4692 | 0.5387 | 0.5604 |
| `S4_hybrid_backbone_enrichment` | 697 | 766 | 567 | 199 | 130 | 0.7402 | 0.8135 | 0.7751 | 0.7178 |

## Template Results

### QT-Q01-AFFECTED-NAS-ELEMENTS

- Question: Which airports, ARTCCs, routes, or other NAS elements are affected by the advisory?
- CQs: CQ-Q01, CQ-D02, CQ-E03
- Predicates: `controlledNASelement`
- Gold answers: 46

| System | P | R | F1 | Evidence coverage | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | 0.4933 | 0.8043 | 0.6116 | 1.0 | `usable_with_review` |
| `S2_llm_schema_slice` | 0.3205 | 0.5435 | 0.4032 | 1.0 | `usable_with_review` |
| `S3_llm_schema_slice_validator_repair` | 0.4561 | 0.5652 | 0.5049 | 0.9649 | `usable_with_review` |
| `S4_hybrid_backbone_enrichment` | 0.4368 | 0.8261 | 0.5714 | 1.0 | `usable_with_review` |

### QT-Q01-TIME-WINDOW

- Question: What are the effective start and end times for the advisory?
- CQs: CQ-Q01, CQ-D03, CQ-O01
- Predicates: `effectiveStartTime`, `effectiveEndTime`
- Gold answers: 196

| System | P | R | F1 | Evidence coverage | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | 0.9796 | 0.9796 | 0.9796 | 1.0 | `ready_for_answer_generation` |
| `S2_llm_schema_slice` | 0.6776 | 0.5255 | 0.592 | 0.9737 | `usable_with_review` |
| `S3_llm_schema_slice_validator_repair` | 0.6053 | 0.2347 | 0.3382 | 0.9211 | `needs_retrieval_or_extraction_review` |
| `S4_hybrid_backbone_enrichment` | 0.9796 | 0.9796 | 0.9796 | 1.0 | `ready_for_answer_generation` |

### QT-Q01-CAUSE-CONDITION

- Question: What weather, volume, runway, equipment, or other condition explains the restriction?
- CQs: CQ-Q01, CQ-E02
- Predicates: `impactingCondition`, `impactingConditionMessage`, `reRouteReason`
- Gold answers: 52

| System | P | R | F1 | Evidence coverage | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | 0.9677 | 0.5769 | 0.7229 | 1.0 | `ready_for_answer_generation` |
| `S2_llm_schema_slice` | 0.6 | 0.75 | 0.6667 | 0.9538 | `usable_with_review` |
| `S3_llm_schema_slice_validator_repair` | 0.7391 | 0.6538 | 0.6939 | 0.9783 | `usable_with_review` |
| `S4_hybrid_backbone_enrichment` | 0.8039 | 0.7885 | 0.7961 | 1.0 | `ready_for_answer_generation` |

### QT-Q01-STATUS-ACTION

- Question: What status or action is stated for the advisory?
- CQs: CQ-Q01, CQ-E01
- Predicates: `implementationStatus`, `initiativeComments`
- Gold answers: 102

| System | P | R | F1 | Evidence coverage | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | 0.7045 | 0.3039 | 0.4247 | 1.0 | `usable_with_review` |
| `S2_llm_schema_slice` | 0.4407 | 0.5098 | 0.4727 | 0.9576 | `usable_with_review` |
| `S3_llm_schema_slice_validator_repair` | 0.6795 | 0.5196 | 0.5889 | 0.9615 | `usable_with_review` |
| `S4_hybrid_backbone_enrichment` | 0.6667 | 0.4706 | 0.5517 | 1.0 | `usable_with_review` |

### QT-Q01-ROUTE-SEMANTICS

- Question: What reroute type, reroute reason, and constrained element are represented?
- CQs: CQ-Q01, CQ-E03, CQ-O02
- Predicates: `reRouteType`, `reRouteReason`, `controlledNASelement`
- Gold answers: 85

| System | P | R | F1 | Evidence coverage | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | 0.4933 | 0.4353 | 0.4625 | 1.0 | `usable_with_review` |
| `S2_llm_schema_slice` | 0.48 | 0.7059 | 0.5714 | 0.968 | `usable_with_review` |
| `S3_llm_schema_slice_validator_repair` | 0.6484 | 0.6941 | 0.6705 | 0.978 | `usable_with_review` |
| `S4_hybrid_backbone_enrichment` | 0.5327 | 0.6706 | 0.5937 | 1.0 | `usable_with_review` |

### QT-A01-ABSTENTION-FIELDS

- Question: Which expected fields are absent or unsupported and should trigger abstention?
- CQs: CQ-A01
- Predicates: `effectiveEndTime`, `extensionProbability`, `impactingCondition`, `reRouteReason`, `controlledNASelement`
- Gold answers: 216

| System | P | R | F1 | Evidence coverage | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | 0.814 | 0.8102 | 0.8121 | 1.0 | `ready_for_answer_generation` |
| `S2_llm_schema_slice` | 0.5591 | 0.6574 | 0.6043 | 0.9685 | `usable_with_review` |
| `S3_llm_schema_slice_validator_repair` | 0.645 | 0.5046 | 0.5662 | 0.9645 | `usable_with_review` |
| `S4_hybrid_backbone_enrichment` | 0.7549 | 0.8843 | 0.8145 | 1.0 | `ready_for_answer_generation` |

## Claim Boundary

This artifact measures whether graph/query outputs can recover source-bounded CQ answers with evidence. It does not claim generated-answer superiority.
