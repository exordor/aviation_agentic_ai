# ATCSCC CQ Query Manifest

- Status: `query_templates_ready`
- Templates: 6
- Boundary: Retrospective FAA ATCSCC advisory KG queries only; no live operational use.

| Template | CQs | Route | Predicates | Metric |
| --- | --- | --- | --- | --- |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | CQ-Q01, CQ-D02, CQ-E03 | `graph_template` | `controlledNASelement` | answer-set precision/recall/F1 plus evidence containment |
| `QT-Q01-TIME-WINDOW` | CQ-Q01, CQ-D03, CQ-O01 | `graph_template` | `effectiveStartTime`, `effectiveEndTime` | time-field answer-set precision/recall/F1 |
| `QT-Q01-CAUSE-CONDITION` | CQ-Q01, CQ-E02 | `graph_template` | `impactingCondition`, `impactingConditionMessage`, `reRouteReason` | condition/reason answer-set precision/recall/F1 |
| `QT-Q01-STATUS-ACTION` | CQ-Q01, CQ-E01 | `hybrid_graph_plus_source_span` | `implementationStatus`, `initiativeComments` | status/comment answer-set precision/recall/F1 |
| `QT-Q01-ROUTE-SEMANTICS` | CQ-Q01, CQ-E03, CQ-O02 | `hybrid_graph_plus_source_span` | `reRouteType`, `reRouteReason`, `controlledNASelement` | route predicate-family answer-set precision/recall/F1 |
| `QT-A01-ABSTENTION-FIELDS` | CQ-A01 | `critic_gate` | `effectiveEndTime`, `extensionProbability`, `impactingCondition`, `reRouteReason`, `controlledNASelement` | false-positive count and abstention-readiness signal |
