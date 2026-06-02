# ATCSCC Technical Implementation Plan

## Baseline Decision

- Accepted current baselines: `S0_rule_only, S4_hybrid_backbone_enrichment`
- Systems requiring review: `S1b_llm_canonicalized, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair`

## Implementation Layers

- deterministic backbone for advisory IDs and normalized times
- schema-slice constrained LLM for semantic enrichment
- validator/repair loop with evidence support as an acceptance criterion
- critic layer for unsupported facts, overclaims, and source-boundary violations
- GraphRAG/query layer only after source-bounded graph materialization is scored

## Profile Gap Signals

| Predicate | Rejected/adjudicated count |
| --- | ---: |
| `impactingConditionMessage` | 17 |
| `controlledNASelement` | 15 |
| `extensionProbability` | 8 |
| `impactingCondition` | 8 |

## Review Gates

- `S1b_llm_canonicalized`: review false-positive and false-negative examples by predicate before `next_live_or_saved_prediction_rerun`.
- `S2_llm_schema_slice`: review schema-slice prompt contract, predicate routing and enum canonicalization, evidence-span preservation before validation, false-positive and false-negative examples by predicate before `next_live_or_saved_prediction_rerun`.
- `S3_llm_schema_slice_validator_repair`: review validator repair rules in atmonto_experiment.py, repair acceptance criteria that may privilege structural validity over semantic support, post-repair evidence support checks, false-positive and false-negative examples by predicate before `next_live_or_saved_prediction_rerun`.
