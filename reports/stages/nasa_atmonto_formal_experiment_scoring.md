# NASA ATMONTO Formal Experiment Scoring

- Status: `pending_required_inputs`
- Protocol: `docs/experiment_protocol.md`

## Gold Source

- Source: `frozen_reviewed_gold_missing`
- Path: `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- Exists: `False`
- Ready for scoring: `False`
- SHA-256: `None`

## Gold Status

- Records: 0
- Reviewed records: 0
- Pending records: 0
- Complete: `False`

## System Metrics

| System | Output | JSON adherence | Candidate facts | Accepted | Rejected | Schema violation rate | Repair success | Semantic metrics |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | `True` | 1.0 | 615 | 567 | 48 | 0.07804878048780488 | 0.9219512195121952 | pending:manual_gold_facts_missing |
| `S1_llm_only` | `False` | None | None | None | None | None | None | pending:prediction_output_missing |
| `S2_llm_schema_slice` | `False` | None | None | None | None | None | None | pending:prediction_output_missing |
| `S3_llm_schema_slice_validator_repair` | `False` | None | None | None | None | None | None | pending:prediction_output_missing |

## Missing Required Inputs

- frozen reviewed gold set at data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl
- completed manual gold annotations for 100 sampled advisories
- S1_llm_only predictions at data/experiments/nasa_atmonto/formal/s1_llm_only_predictions.jsonl
- S2_llm_schema_slice predictions at data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_predictions.jsonl
- S3_llm_schema_slice_validator_repair predictions at data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_predictions.jsonl
- manual semantic metrics require reviewed gold facts

## Boundary

- Formal metrics are descriptive until all four systems have predictions and the frozen reviewed gold set is available.
