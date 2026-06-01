# NASA ATMONTO Formal Experiment Readiness

- Status: `ready_for_manual_gold_and_llm_runs`
- Protocol: `docs/experiment_protocol.md`
- Gold manifest: `data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json`
- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`

## Gold Status

- Records: 100
- Reviewed records: 0
- Pending records: 100
- Complete: `False`
- Status counts: `{"pending_manual_gold_annotation": 100}`

## Systems

- `S0_rule_only`: Rule-only (LLM=False, schema=True, repair=False)
- `S1_llm_only`: LLM-only (LLM=True, schema=False, repair=False)
- `S2_llm_schema_slice`: LLM + schema slice (LLM=True, schema=True, repair=False)
- `S3_llm_schema_slice_validator_repair`: LLM + schema slice + validator/repair (LLM=True, schema=True, repair=True)

## Current S0 Structural Metrics

- `attempted_record_count`: 100
- `valid_json_payload_count`: 100
- `json_adherence`: 1.0
- `candidate_fact_count`: 615
- `accepted_fact_count`: 567
- `rejected_fact_count`: 48
- `schema_violation_rate`: 0.07804878048780488
- `repair_success_rate`: 0.9219512195121952

## Missing Required Inputs

- completed manual gold annotations for 100 sampled advisories
- S1_llm_only predictions at data/experiments/nasa_atmonto/formal/s1_llm_only_predictions.jsonl
- S2_llm_schema_slice predictions at data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_predictions.jsonl
- S3_llm_schema_slice_validator_repair predictions at data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_predictions.jsonl

## Boundary

- This readiness report does not claim formal extraction effectiveness until manual gold annotations and S1-S3 outputs are present.
