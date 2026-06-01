# NASA ATMONTO Prediction Output Validation

- Status: `pending_required_outputs`
- Selected source IDs: 100
- Errors: 0
- Pending items: 6

## Completion Gate

- Prediction outputs are usable for formal scoring only when every system status is ready_for_scoring.

## Systems

| System | Status | Output | Run Metadata | JSON adherence | Missing records | Pending | Errors |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `S0_rule_only` | `ready_for_scoring` | `True` | `True` | 1.0 | 0 | `` | `` |
| `S1_llm_only` | `pending_required_outputs` | `False` | `False` | None | None | `prediction_output_missing, run_metadata_missing` | `` |
| `S2_llm_schema_slice` | `pending_required_outputs` | `False` | `False` | None | None | `prediction_output_missing, run_metadata_missing` | `` |
| `S3_llm_schema_slice_validator_repair` | `pending_required_outputs` | `False` | `False` | None | None | `prediction_output_missing, run_metadata_missing` | `` |
