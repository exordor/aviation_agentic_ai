# ATCSCC Extraction Plan

## Extraction Boundary

- Extract only source-bounded ATCSCC advisory facts required by the 12 primary CQs.
- Preserve deterministic backbone fields before LLM semantic enrichment.
- Route unsupported or ambiguous facts to abstention or repair; do not complete from common sense.

## Required Schema Fields

- Top-level fields: `source_id, facts`
- Fact fields: `fact_id, fact_type, subject, subject_class, predicate, evidence_text`
- Available fact fields: `datatype, evidence_text, fact_id, fact_type, object, object_class, predicate, subject, subject_class, value`

## Predicate Coverage Plan

| Predicate | CQ mentions | Extraction route | Evidence rule |
| --- | ---: | --- | --- |
| `controlledNASelement` | 4 | `hybrid` | Require source ID and advisory text excerpt. |
| `reRouteReason` | 4 | `hybrid` | Require source ID and advisory text excerpt. |
| `effectiveEndTime` | 3 | `hybrid` | Require source ID and advisory text excerpt. |
| `evidence_text` | 3 | `hybrid` | Require source ID and advisory text excerpt. |
| `impactingCondition` | 3 | `hybrid` | Require source ID and advisory text excerpt. |
| `initiativeComments` | 3 | `hybrid` | Require source ID and advisory text excerpt. |
| `advisoryNumber` | 2 | `deterministic/backbone` | Require source ID and advisory text excerpt. |
| `effectiveStartTime` | 2 | `hybrid` | Require source ID and advisory text excerpt. |
| `extensionProbability` | 2 | `hybrid` | Require source ID and advisory text excerpt. |
| `impactingConditionMessage` | 2 | `hybrid` | Require source ID and advisory text excerpt. |
| `implementationStatus` | 2 | `hybrid` | Require source ID and advisory text excerpt. |
| `issuedTime` | 2 | `hybrid` | Require source ID and advisory text excerpt. |
| `reRouteType` | 2 | `hybrid` | Require source ID and advisory text excerpt. |
| `source_id` | 2 | `hybrid` | Require source ID and advisory text excerpt. |
| `rdf:type` | 1 | `deterministic/backbone` | Require source ID and advisory text excerpt. |

## Implementation Layers

- deterministic backbone for advisory IDs and normalized times
- schema-slice constrained LLM for semantic enrichment
- validator/repair loop with evidence support as an acceptance criterion
- critic layer for unsupported facts, overclaims, and source-boundary violations
- GraphRAG/query layer only after source-bounded graph materialization is scored

## Abstention Rules

- Missing field in the advisory: emit an explicit absent/unknown label only when the CQ requires it.
- Unsupported value: quarantine rather than repair.
- Out-of-profile predicate: report as a profile gap, not as existing ATMONTO truth.
