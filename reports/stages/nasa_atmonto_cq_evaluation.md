# NASA ATMONTO CQ Evaluation Mapping

## Scope

- Gold set: `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- Scoring report: `reports/stages/nasa_atmonto_formal_experiment_scoring.json`
- Semantic groups: `reports/stages/nasa_atmonto_gold_semantic_groups.json`
- Rejection adjudication: `reports/stages/nasa_atmonto_rejection_adjudication.json`
- Boundary: Retrospective FAA ATCSCC advisory extraction only; no live operational use.

## Gold Coverage Snapshot

- Reviewed records: 100/100
- Gold facts: 651 (470 accepted, 181 reviewed missing)
- Invalid candidate facts: 104
- Rejected-fact adjudications: 40
- Evidence containment: 651/651 checked (1.0)

### Candidate Subject Classes

| Class | Records |
| --- | ---: |
| `TrafficManagementInitiative` | 40 |
| `ReRouteTMI` | 23 |
| `GroundStopTMI` | 21 |
| `GroundDelayProgramTMI` | 16 |

### Top Gold Predicates

| Predicate | Gold facts | Accepted | Reviewed missing | Records |
| --- | ---: | ---: | ---: | ---: |
| `advisoryNumber` | 100 | 92 | 8 | 100 |
| `effectiveEndTime` | 98 | 91 | 7 | 98 |
| `effectiveStartTime` | 98 | 91 | 7 | 98 |
| `issuedTime` | 98 | 72 | 26 | 98 |
| `initiativeComments` | 81 | 24 | 57 | 81 |
| `controlledNASelement` | 46 | 36 | 10 | 45 |
| `extensionProbability` | 30 | 21 | 9 | 30 |
| `impactingCondition` | 30 | 27 | 3 | 30 |
| `implementationStatus` | 21 | 6 | 15 | 21 |
| `reRouteReason` | 20 | 0 | 20 | 20 |
| `reRouteType` | 19 | 0 | 19 | 19 |
| `impactingConditionMessage` | 10 | 10 | 0 | 10 |

## CQ Evaluation Matrix

| CQ | Role | Status | Gold coverage | Best current system | F1 | Main gap |
| --- | --- | --- | ---: | --- | ---: | --- |
| `CQ-D01` | Domain typing | `partially_measurable_now` | 100 | `n/a` | n/a | Per-system primary-class accuracy is not yet scored as a first-class metric. |
| `CQ-D02` | Entity role | `directly_measurable_now` | 46 | `S0_rule_only` | 0.595 | ARTCC controlled-element facts remain profile gaps until a reviewed bridge exists. |
| `CQ-D03` | Temporal semantics | `directly_measurable_now` | 294 | `S4_hybrid_backbone_enrichment` | 0.8639 | The report can score exact values but does not yet isolate rollover-specific errors. |
| `CQ-E01` | Status/action | `directly_measurable_now` | 102 | `S4_hybrid_backbone_enrichment` | 0.4433 | Status labels are sparse, so comments evidence remains important context. |
| `CQ-E02` | Cause/condition | `directly_measurable_now` | 141 | `S0_rule_only` | 0.5072 | Some source-supported causes remain outside the current controlled vocabulary. |
| `CQ-E03` | Route/airspace semantics | `directly_measurable_now` | 166 | `S0_rule_only` | 0.4316 | AFP/CTOP semantics remain deferred unless the profile and sample support them. |
| `CQ-O01` | Core conformance | `directly_measurable_now` | 394 | `S4_hybrid_backbone_enrichment` | 0.8782 | Schema conformance is separate from semantic support and must not be treated as truth. |
| `CQ-O02` | Type-specific conformance | `directly_measurable_now` | 79 | `S4_hybrid_backbone_enrichment` | 0.6076 | Accepted profile extensions require reviewed ontology/profile changes. |
| `CQ-P01` | Evidence coverage | `directly_measurable_now` | 651 | `n/a` | n/a | The current contract stores evidence text, not stable character offsets. |
| `CQ-P02` | Evidence support | `directly_measurable_now` | 651 | `n/a` | n/a | Value-support judgement remains a reviewed semantic metric, not pure SHACL validation. |
| `CQ-Q01` | Source-bounded queryability | `partially_measurable_now` | 293 | `S0_rule_only` | 0.8223 | Template graph queries over the frozen KG are not yet materialized as a scored artifact. |
| `CQ-A01` | Abstention | `partially_measurable_now` | 224 | `S0_rule_only` | 0.7608 | The gold set exposes false positives, but explicit absent-field labels need a follow-up pass. |

## System-Level Metrics

- `S0_rule_only`: precision=0.8163, recall=0.7097, f1=0.7592, validity=`valid_target_schema_scoring`
- `S1_llm_only`: precision=0.0, recall=0.0, f1=0.0, validity=`invalid_direct_schema_scoring`
- `S1b_llm_canonicalized`: precision=0.4974, recall=0.1444, f1=0.2238, validity=`valid_target_schema_scoring`
- `S2_llm_schema_slice`: precision=0.2062, recall=0.1843, f1=0.1946, validity=`valid_target_schema_scoring`
- `S3_llm_schema_slice_validator_repair`: precision=0.2423, recall=0.1321, f1=0.171, validity=`valid_target_schema_scoring`
- `S4_hybrid_backbone_enrichment`: precision=0.6795, recall=0.7619, f1=0.7183, validity=`valid_target_schema_scoring`

## Rejection Boundary

- Property-level complete: True
- Rejected facts: 288
- Pending facts: 0
- Decisions: `{"extractor_bug": 13, "profile_gap": 275}`

## Next Experiment Steps

- Add primary-class accuracy scoring for CQ-D01 instead of relying on class coverage.
- Materialize frozen-snapshot template queries for CQ-Q01 and score answer-set precision/recall.
- Add explicit absent-field labels or derived negative examples for CQ-A01 abstention correctness.
- Keep ARTCC controlled-element profile gaps separate from accepted facts until a reviewed bridge exists.
