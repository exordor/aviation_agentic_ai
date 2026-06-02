# ATCSCC Extraction-Validation Plan

## Loop Policy

- Normal step: run extractor -> validator -> critic -> repair/abstain -> score
- Abnormal step: if anomaly_flags are emitted, review code or artifact contract before rerun
- Hard rule: Do not explain abnormal results without routing them to review_code or review_artifact.

## System Routing

| System | Action | Flags |
| --- | --- | --- |
| `S0_rule_only` | `accept_for_current_baseline` | `none` |
| `S1_llm_only` | `quarantine_before_rerun` | `invalid_target_schema_scoring, schema_rejection_collapse, structural_acceptance_low, semantic_f1_below_minimum` |
| `S1b_llm_canonicalized` | `review_code_before_rerun` | `structural_acceptance_low, semantic_f1_below_minimum` |
| `S2_llm_schema_slice` | `review_code_before_rerun` | `structural_acceptance_low, semantic_f1_below_minimum` |
| `S3_llm_schema_slice_validator_repair` | `review_code_before_rerun` | `semantic_f1_below_minimum, repair_did_not_improve_semantic_f1, structural_repair_without_semantic_gain` |
| `S4_hybrid_backbone_enrichment` | `accept_for_current_baseline` | `none` |

## Next Actions

- Review code paths listed in code_review_triggers before rerunning S2/S3 extraction.
- Use the generated SRD and TIP as the contract before another live LLM run.
- Materialize template graph queries for CQ-Q01 before making GraphRAG answer-quality claims.
- Add explicit absent-field labels for CQ-A01 if abstention becomes a primary claim.
