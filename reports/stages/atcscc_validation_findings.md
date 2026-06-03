# ATCSCC Validation Findings

## Prediction Output Readiness

- Status: `ready_for_scoring`
- Selected source IDs: `100`
- Error count: `0`
- Pending count: `0`

## Agentic Loop Diagnostics

| System | F1 | Schema violation | Structural acceptance | JSON adherence | Action | Flags |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `S0_rule_only` | 0.7643 | 0.078 | 0.922 | 1.0 | `accept_for_current_baseline` | `none` |
| `S1_llm_only` | 0.0 | 1.0 | 0.0 | 1.0 | `quarantine_before_rerun` | `invalid_target_schema_scoring, schema_rejection_collapse, structural_acceptance_low, semantic_f1_below_minimum` |
| `S1b_llm_canonicalized` | 0.2271 | 0.5925 | 0.4075 | 1.0 | `review_code_before_rerun` | `structural_acceptance_low, semantic_f1_below_minimum` |
| `S2_llm_schema_slice` | 0.1959 | 0.1751 | 0.8249 | 1.0 | `review_code_before_rerun` | `semantic_f1_below_minimum` |
| `S3_llm_schema_slice_validator_repair` | 0.1723 | 0.1035 | 0.8965 | 1.0 | `review_code_before_rerun` | `semantic_f1_below_minimum, repair_did_not_improve_semantic_f1, structural_repair_without_semantic_gain` |
| `S4_hybrid_backbone_enrichment` | 0.7395 | 0.0 | 1.0 | 1.0 | `accept_for_current_baseline` | `none` |

## Code Review Triggers

- `S1b_llm_canonicalized`: flags=`structural_acceptance_low, semantic_f1_below_minimum`; focus=false-positive and false-negative examples by predicate
- `S2_llm_schema_slice`: flags=`semantic_f1_below_minimum`; focus=schema-slice prompt contract; predicate routing and enum canonicalization; evidence-span preservation before validation; false-positive and false-negative examples by predicate
- `S3_llm_schema_slice_validator_repair`: flags=`semantic_f1_below_minimum, repair_did_not_improve_semantic_f1, structural_repair_without_semantic_gain`; focus=validator repair rules in atmonto_experiment.py; repair acceptance criteria that may privilege structural validity over semantic support; post-repair evidence support checks; false-positive and false-negative examples by predicate

## Validation Boundary

- Schema validity is not semantic truth.
- Semantic correctness is not operational readiness.
- Abnormal metrics trigger code or artifact review before another extraction run.
