# NASA ATMONTO Formal Experiment Readiness

- Status: `ready_for_scoring`
- Protocol: `docs/experiment_protocol.md`
- Gold manifest: `data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json`
- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Workload plan: `reports/stages/nasa_atmonto_gold_review_workload_plan.md`
- Semantic groups: `reports/stages/nasa_atmonto_gold_semantic_groups.md`
- Session plan: `reports/stages/nasa_atmonto_gold_review_session_plan.md`
- Priority packets: `data/evaluation/nasa_atmonto/review_priority_packets/index.md`
- Review progress: `data/evaluation/nasa_atmonto/gold_review_progress.md`

## Gold Status

- Records: 100
- Reviewed records: 100
- Pending records: 0
- Complete: `True`
- Status counts: `{"reviewed": 100}`

## Manual Gold Review Kickoff

- Status: `complete`
- Reviewed / pending records: 100 / 0
- Decision progress: `ready_to_apply`
- Ready to apply / not started: 100 / 0
- Rejected-fact decisions confirmed: 48 / 48
- First priority lane: `1_rejection_adjudication` (40 records, 808 est. min)
- Start packet: `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md`
- First sample: `ATCSCC-GOLD-024` / `2026-05-18:136` via `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Boundary: Priority packets and suggested_* fields are work aids only. A record becomes gold only after source review, completed review_checklist, confirmed decisions, validation, and frozen reviewed output.
- Next review session: `none`; gold review is complete.

### Next Commands

- `uv run python scripts/prepare_nasa_atmonto_gold_review_decision_progress.py`
- `uv run python scripts/apply_nasa_atmonto_gold_review_decisions.py`
- `uv run python scripts/validate_nasa_atmonto_gold_annotations.py`
- `uv run python scripts/freeze_nasa_atmonto_gold_set.py`
- `uv run python scripts/run_nasa_atmonto_formal_experiment.py --skip-prepare-inputs`

## Formal Inputs

- Input records: `data/experiments/nasa_atmonto/formal/input_records.jsonl`
- Input records exists: `True`
- System specs: `data/experiments/nasa_atmonto/formal/system_specs.json`
- System specs exists: `True`

## Systems

- `S0_rule_only`: Rule-only (LLM=False, schema=True, repair=False, prompt_ready=None, output_ready=True)
- `S1_llm_only`: LLM-only (LLM=True, schema=False, repair=False, prompt_ready=True, output_ready=True)
- `S2_llm_schema_slice`: LLM + schema slice (LLM=True, schema=True, repair=False, prompt_ready=True, output_ready=True)
- `S3_llm_schema_slice_validator_repair`: LLM + schema slice + validator/repair (LLM=True, schema=True, repair=True, prompt_ready=True, output_ready=True)

## Current S0 Structural Metrics

- `attempted_record_count`: 100
- `valid_json_payload_count`: 100
- `json_adherence`: 1.0
- `candidate_fact_count`: 615
- `accepted_fact_count`: 567
- `rejected_fact_count`: 48
- `structural_acceptance_rate`: 0.9219512195121952
- `schema_violation_rate`: 0.07804878048780488
- `repair_applicable`: False
- `repair_attempted_fact_count`: n/a
- `repair_accepted_fact_count`: n/a
- `repair_success_rate`: n/a

## Missing Required Inputs


## Boundary

- This readiness report does not claim formal extraction effectiveness until manual gold annotations are complete and all required system outputs are present.
