# NASA ATMONTO Prediction Output Validation

- Status: `ready_for_scoring`
- Selected source IDs: 100
- Errors: 0
- Pending items: 0

## Completion Gate

- Prediction outputs are usable for formal scoring only when every system status is ready_for_scoring.

## Systems

| System | Status | Output | Run Metadata | JSON adherence | Missing records | Normalizer | Flattened facts | Schema-valid records | Pending | Errors |
| --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| `S0_rule_only` | `ready_for_scoring` | `True` | `True` | 1.0 | 0 | `` |  |  | `` | `` |
| `S1_llm_only` | `ready_for_scoring` | `True` | `True` | 1.0 | 0 | `schema_object_flattening_v1` | 0 | 0 | `` | `` |
| `S1b_llm_canonicalized` | `ready_for_scoring` | `True` | `True` | 1.0 | 0 | `schema_object_flattening_v1` | 0 | 32 | `` | `` |
| `S2_llm_schema_slice` | `ready_for_scoring` | `True` | `True` | 1.0 | 0 | `schema_object_flattening_v1` | 465 | 67 | `` | `` |
| `S3_llm_schema_slice_validator_repair` | `ready_for_scoring` | `True` | `True` | 1.0 | 0 | `schema_object_flattening_v1` | 321 | 83 | `` | `` |
| `S4_hybrid_backbone_enrichment` | `ready_for_scoring` | `True` | `True` | 1.0 | 0 | `schema_object_flattening_v1` | 0 | 100 | `` | `` |
