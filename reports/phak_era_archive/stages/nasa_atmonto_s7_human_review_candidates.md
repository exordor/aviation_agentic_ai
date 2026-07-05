# NASA ATMONTO S7 Human Review Candidate Package

## Boundary

This is a candidate package for human or supervisor review. It is not human-reviewed evidence until an external reviewer records decisions.

## Summary

- Source LLM cases: 60
- Failure candidates: 3
- Coverage success candidates: 6
- Candidate total: 9

## Candidate Index

| Review ID | Priority | Template | Mode | Source | Correct | Unsupported |
| --- | --- | --- | --- | --- | ---: | ---: |
| `S7-HR-001` | failure | `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_live_tfidf_graphrag` | `2026-05-15:067` | False | 0.5 |
| `S7-HR-002` | failure | `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_dense_graphrag` | `2026-05-15:067` | False | 0.5 |
| `S7-HR-003` | failure | `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_dense_graphrag` | `2026-05-15:064` | False | 0.5 |
| `S7-HR-004` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_token_matched_live_tfidf_graphrag` | `2026-05-19:079` | True | 0.0 |
| `S7-HR-005` | coverage_success | `QT-Q01-TIME-WINDOW` | `routed_token_matched_live_tfidf_graphrag` | `2026-05-19:032` | True | 0.0 |
| `S7-HR-006` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_live_tfidf_graphrag` | `2026-05-19:079` | True | 0.0 |
| `S7-HR-007` | coverage_success | `QT-Q01-STATUS-ACTION` | `routed_token_matched_live_tfidf_graphrag` | `2026-05-19:032` | True | 0.0 |
| `S7-HR-008` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `routed_token_matched_live_tfidf_graphrag` | `2026-05-19:079` | True | 0.0 |
| `S7-HR-009` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `routed_token_matched_live_tfidf_graphrag` | `2026-05-19:032` | True | 0.0 |

## Candidate Details

### S7-HR-001 - failure

- Template: `QT-Q01-CAUSE-CONDITION`
- Mode: `routed_token_matched_live_tfidf_graphrag`
- Source: `2026-05-15:067`
- Question: What weather, volume, runway, equipment, or other condition explains the restriction?
- Expected: `impactingConditionMessage=STAFFING / STAFFING`
- Answer values: `[{'predicate': 'impactingCondition', 'value': 'staffing'}, {'predicate': 'impactingConditionMessage', 'value': 'STAFFING / STAFFING'}]`
- Metrics: correctness=False, faithfulness=False, unsupported=0.5

**Evidence Chunks**

- `atcscc-2026-05-15-067-p1-c1`: IMPACTING CONDITION: STAFFING / STAFFING

**Graph Triples**

- `t1` impactingCondition=other | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45
- `t2` impactingConditionMessage=STAFFING / STAFFING | IMPACTING CONDITION: STAFFING / STAFFING

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?
- If incorrect, is the issue model over-answer, retrieval context, or label/profile design?
- Which returned predicate/value pair is unsupported or out of profile?

### S7-HR-002 - failure

- Template: `QT-Q01-CAUSE-CONDITION`
- Mode: `routed_token_matched_dense_graphrag`
- Source: `2026-05-15:067`
- Question: What weather, volume, runway, equipment, or other condition explains the restriction?
- Expected: `impactingConditionMessage=STAFFING / STAFFING`
- Answer values: `[{'predicate': 'impactingCondition', 'value': 'other'}, {'predicate': 'impactingConditionMessage', 'value': 'STAFFING / STAFFING'}]`
- Metrics: correctness=False, faithfulness=False, unsupported=0.5

**Evidence Chunks**

- `atcscc-2026-05-15-067-p1-c1`: IMPACTING CONDITION: STAFFING / STAFFING

**Graph Triples**

- `t1` impactingCondition=other | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45
- `t2` impactingConditionMessage=STAFFING / STAFFING | IMPACTING CONDITION: STAFFING / STAFFING

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?
- If incorrect, is the issue model over-answer, retrieval context, or label/profile design?
- Which returned predicate/value pair is unsupported or out of profile?

### S7-HR-003 - failure

- Template: `QT-Q01-CAUSE-CONDITION`
- Mode: `routed_token_matched_dense_graphrag`
- Source: `2026-05-15:064`
- Question: What weather, volume, runway, equipment, or other condition explains the restriction?
- Expected: `impactingConditionMessage=STAFFING / STAFFING`
- Answer values: `[{'predicate': 'impactingCondition', 'value': 'staffing'}, {'predicate': 'impactingConditionMessage', 'value': 'STAFFING / STAFFING'}]`
- Metrics: correctness=False, faithfulness=False, unsupported=0.5

**Evidence Chunks**

- `atcscc-2026-05-15-064-p1-c1`: IMPACTING CONDITION: STAFFING / STAFFING

**Graph Triples**

- `t1` impactingCondition=other | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY.
- `t2` impactingConditionMessage=STAFFING / STAFFING | IMPACTING CONDITION: STAFFING / STAFFING

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?
- If incorrect, is the issue model over-answer, retrieval context, or label/profile design?
- Which returned predicate/value pair is unsupported or out of profile?

### S7-HR-004 - coverage_success

- Template: `QT-Q01-AFFECTED-NAS-ELEMENTS`
- Mode: `routed_token_matched_live_tfidf_graphrag`
- Source: `2026-05-19:079`
- Question: Which airports, ARTCCs, routes, or other NAS elements are affected by the advisory?
- Expected: `controlledNASelement=BNA`
- Answer values: `[{'predicate': 'controlledNASelement', 'value': 'BNA'}]`
- Metrics: correctness=True, faithfulness=True, unsupported=0.0

**Evidence Chunks**

- `atcscc-2026-05-19-079-p1-c1`: CTL ELEMENT: BNA

**Graph Triples**

- `t1` controlledNASelement=BNA | CTL ELEMENT: BNA

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?

### S7-HR-005 - coverage_success

- Template: `QT-Q01-TIME-WINDOW`
- Mode: `routed_token_matched_live_tfidf_graphrag`
- Source: `2026-05-19:032`
- Question: What are the effective start and end times for the advisory?
- Expected: `effectiveStartTime=2026-05-19T13:22:00Z, effectiveEndTime=2026-05-19T16:30:00Z`
- Answer values: `[{'predicate': 'effectiveStartTime', 'value': '2026-05-19T13:22:00Z'}, {'predicate': 'effectiveEndTime', 'value': '2026-05-19T16:30:00Z'}]`
- Metrics: correctness=True, faithfulness=True, unsupported=0.0

**Evidence Chunks**

- `atcscc-2026-05-19-032-p1-c1`: EFFECTIVE TIME: 191322-191630 EFFECTIVE TIME: 191322-191630
- `atcscc-2026-05-20-150-p1-c1`: source_id 2026-05-20:150

**Graph Triples**

- none

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?

### S7-HR-006 - coverage_success

- Template: `QT-Q01-CAUSE-CONDITION`
- Mode: `routed_token_matched_live_tfidf_graphrag`
- Source: `2026-05-19:079`
- Question: What weather, volume, runway, equipment, or other condition explains the restriction?
- Expected: `impactingConditionMessage=STAFFING / STAFFING`
- Answer values: `[{'predicate': 'impactingConditionMessage', 'value': 'STAFFING / STAFFING'}]`
- Metrics: correctness=True, faithfulness=True, unsupported=0.0

**Evidence Chunks**

- `atcscc-2026-05-19-079-p1-c1`: IMPACTING CONDITION: STAFFING / STAFFING

**Graph Triples**

- `t1` impactingConditionMessage=STAFFING / STAFFING | IMPACTING CONDITION: STAFFING / STAFFING

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?

### S7-HR-007 - coverage_success

- Template: `QT-Q01-STATUS-ACTION`
- Mode: `routed_token_matched_live_tfidf_graphrag`
- Source: `2026-05-19:032`
- Question: What status or action is stated for the advisory?
- Expected: `implementationStatus=RQD`
- Answer values: `[{'predicate': 'implementationStatus', 'value': 'RQD'}]`
- Metrics: correctness=True, faithfulness=True, unsupported=0.0

**Evidence Chunks**

- `atcscc-2026-05-19-032-p1-c1`: _RQD

**Graph Triples**

- `t1` implementationStatus=RQD | _RQD

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?

### S7-HR-008 - coverage_success

- Template: `QT-Q01-ROUTE-SEMANTICS`
- Mode: `routed_token_matched_live_tfidf_graphrag`
- Source: `2026-05-19:079`
- Question: What reroute type, reroute reason, and constrained element are represented?
- Expected: `controlledNASelement=BNA`
- Answer values: `[{'predicate': 'controlledNASelement', 'value': 'BNA'}]`
- Metrics: correctness=True, faithfulness=True, unsupported=0.0

**Evidence Chunks**

- `atcscc-2026-05-19-079-p1-c1`: CTL ELEMENT: BNA

**Graph Triples**

- `t1` controlledNASelement=BNA | CTL ELEMENT: BNA

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?

### S7-HR-009 - coverage_success

- Template: `QT-A01-ABSTENTION-FIELDS`
- Mode: `routed_token_matched_live_tfidf_graphrag`
- Source: `2026-05-19:032`
- Question: Which expected fields are absent or unsupported and should trigger abstention?
- Expected: `absent:controlledNASelement, absent:extensionProbability, absent:impactingCondition, absent:reRouteReason`
- Answer values: `[]`
- Metrics: correctness=True, faithfulness=True, unsupported=0.0

**Evidence Chunks**

- `atcscc-2026-05-19-032-p1-c1`: EFFECTIVE TIME: 191322-191630
- `atcscc-2026-05-18-075-p1-c1`: source_id 2026-05-18:075 advisory_date 2026-05-18 advisory_number 75 ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSC

**Graph Triples**

- none

**Review Questions**

- Does each answer value appear directly supported by the cited source span or graph triple?
- Does the answer include only predicates required by the CQ template and current profile?
- Are citations sufficient to trace the answer back to source evidence?
- Should this case abstain, or is there enough evidence for a bounded partial answer?


## Claim Boundary

Use this package to inspect source support, over-answer behavior, citation quality, and ontology/profile boundary cases. Do not cite it as expert certification.
