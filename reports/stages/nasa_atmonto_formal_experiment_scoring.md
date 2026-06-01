# NASA ATMONTO Formal Experiment Scoring

- Status: `scored`
- Protocol: `docs/experiment_protocol.md`

## Gold Source

- Source: `frozen_reviewed_gold`
- Path: `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- Exists: `True`
- Ready for scoring: `True`
- SHA-256: `8acc589642c59b1be9bd00e9d9d636900c41de1c2985f6e8957ec02606f8289a`

## Gold Status

- Records: 100
- Reviewed records: 100
- Pending records: 0
- Complete: `True`

## System Metrics

| System | Output | JSON adherence | Candidate facts | Accepted | Rejected | Structural acceptance | Schema violation rate | Repair success | Semantic metrics |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | `True` | 1.0 | 615 | 567 | 48 | 0.9219512195121952 | 0.07804878048780488 | n/a | P=0.8162544169611308, R=0.71850699844479, F1=0.7642679900744418 |
| `S1_llm_only` | `True` | 1.0 | 1211 | 0 | 1211 | 0.0 | 1.0 | n/a | P=0.0, R=0.0, F1=0.0 |
| `S2_llm_schema_slice` | `True` | 1.0 | 708 | 361 | 347 | 0.5098870056497176 | 0.4901129943502825 | n/a | P=0.233983286908078, R=0.13063763608087092, F1=0.16766467065868265 |
| `S3_llm_schema_slice_validator_repair` | `True` | 1.0 | 396 | 286 | 110 | 0.7222222222222222 | 0.2777777777777778 | 0.7222222222222222 | P=0.26223776223776224, R=0.1166407465007776, F1=0.16146393972012918 |

## Semantic Confidence Intervals

| System | Method | Precision 95% CI | Recall 95% CI | F1 95% CI |
| --- | --- | ---: | ---: | ---: |
| `S0_rule_only` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.7534246575342466 - 0.8619329388560157 | 0.6656200941915228 - 0.7770992366412214 | 0.712280701754386 - 0.8097560975609756 |
| `S1_llm_only` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.0 - 0.0 | 0.0 - 0.0 | 0.0 - 0.0 |
| `S2_llm_schema_slice` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.17086834733893558 - 0.3011049723756906 | 0.08605341246290801 - 0.17425431711145997 | 0.11391018619934283 - 0.21448730009407338 |
| `S3_llm_schema_slice_validator_repair` | `record_bootstrap_by_source_id` (200 iter, seed=1701) | 0.1791044776119403 - 0.3432203389830508 | 0.07258064516129033 - 0.1529051987767584 | 0.10238907849829351 - 0.20972972972972972 |

## Semantic Group Metrics

- Semantic groups are stratified reporting slices, not train/dev/test splits.

| System | Group | Records | Gold facts | Predicted facts | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `S0_rule_only` | `ground_stop_lifecycle` | 26 | 183 | 190 | 0.8736842105263158 | 0.907103825136612 | 0.8900804289544235 |
| `S0_rule_only` | `reroute_or_route_constraint` | 25 | 183 | 113 | 0.8938053097345132 | 0.5519125683060109 | 0.6824324324324325 |
| `S0_rule_only` | `volcanic_activity_bulletin` | 19 | 95 | 76 | 0.75 | 0.6 | 0.6666666666666665 |
| `S0_rule_only` | `ground_delay_program_lifecycle` | 12 | 86 | 87 | 0.9885057471264368 | 1.0 | 0.9942196531791908 |
| `S0_rule_only` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 63 | 0.6349206349206349 | 0.7272727272727273 | 0.6779661016949152 |
| `S0_rule_only` | `hotline_or_webpage_status` | 3 | 15 | 12 | 0.3333333333333333 | 0.26666666666666666 | 0.2962962962962963 |
| `S0_rule_only` | `airport_diversion_recovery` | 2 | 12 | 8 | 0.0 | 0.0 | 0.0 |
| `S0_rule_only` | `special_or_flow_constraint_fyi` | 2 | 10 | 9 | 0.4444444444444444 | 0.4 | 0.4210526315789474 |
| `S0_rule_only` | `flight_plan_drop_time_status` | 1 | 4 | 8 | 0.5 | 1.0 | 0.6666666666666666 |
| `S1_llm_only` | `ground_stop_lifecycle` | 26 | 183 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `reroute_or_route_constraint` | 25 | 183 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `volcanic_activity_bulletin` | 19 | 95 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `ground_delay_program_lifecycle` | 12 | 86 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `hotline_or_webpage_status` | 3 | 15 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `airport_diversion_recovery` | 2 | 12 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `special_or_flow_constraint_fyi` | 2 | 10 | 0 | 0.0 | 0.0 | 0.0 |
| `S1_llm_only` | `flight_plan_drop_time_status` | 1 | 4 | 0 | 0.0 | 0.0 | 0.0 |
| `S2_llm_schema_slice` | `ground_stop_lifecycle` | 26 | 183 | 99 | 0.31313131313131315 | 0.16939890710382513 | 0.2198581560283688 |
| `S2_llm_schema_slice` | `reroute_or_route_constraint` | 25 | 183 | 130 | 0.18461538461538463 | 0.13114754098360656 | 0.15335463258785942 |
| `S2_llm_schema_slice` | `volcanic_activity_bulletin` | 19 | 95 | 38 | 0.5263157894736842 | 0.21052631578947367 | 0.3007518796992481 |
| `S2_llm_schema_slice` | `ground_delay_program_lifecycle` | 12 | 86 | 33 | 0.030303030303030304 | 0.011627906976744186 | 0.01680672268907563 |
| `S2_llm_schema_slice` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 34 | 0.08823529411764706 | 0.05454545454545454 | 0.06741573033707865 |
| `S2_llm_schema_slice` | `hotline_or_webpage_status` | 3 | 15 | 13 | 0.15384615384615385 | 0.13333333333333333 | 0.14285714285714288 |
| `S2_llm_schema_slice` | `airport_diversion_recovery` | 2 | 12 | 6 | 0.5 | 0.25 | 0.3333333333333333 |
| `S2_llm_schema_slice` | `special_or_flow_constraint_fyi` | 2 | 10 | 0 | 0.0 | 0.0 | 0.0 |
| `S2_llm_schema_slice` | `flight_plan_drop_time_status` | 1 | 4 | 6 | 0.0 | 0.0 | 0.0 |
| `S3_llm_schema_slice_validator_repair` | `ground_stop_lifecycle` | 26 | 183 | 67 | 0.2537313432835821 | 0.09289617486338798 | 0.136 |
| `S3_llm_schema_slice_validator_repair` | `reroute_or_route_constraint` | 25 | 183 | 103 | 0.3786407766990291 | 0.21311475409836064 | 0.2727272727272727 |
| `S3_llm_schema_slice_validator_repair` | `volcanic_activity_bulletin` | 19 | 95 | 12 | 0.5 | 0.06315789473684211 | 0.11214953271028039 |
| `S3_llm_schema_slice_validator_repair` | `ground_delay_program_lifecycle` | 12 | 86 | 48 | 0.125 | 0.06976744186046512 | 0.08955223880597014 |
| `S3_llm_schema_slice_validator_repair` | `airport_arrival_or_scheduling_delay` | 10 | 55 | 26 | 0.11538461538461539 | 0.05454545454545454 | 0.07407407407407408 |
| `S3_llm_schema_slice_validator_repair` | `hotline_or_webpage_status` | 3 | 15 | 11 | 0.0 | 0.0 | 0.0 |
| `S3_llm_schema_slice_validator_repair` | `airport_diversion_recovery` | 2 | 12 | 11 | 0.36363636363636365 | 0.3333333333333333 | 0.34782608695652173 |
| `S3_llm_schema_slice_validator_repair` | `special_or_flow_constraint_fyi` | 2 | 10 | 5 | 0.0 | 0.0 | 0.0 |
| `S3_llm_schema_slice_validator_repair` | `flight_plan_drop_time_status` | 1 | 4 | 3 | 0.0 | 0.0 | 0.0 |

## Rejection Adjudication

- Property-level complete: `True`
- Decision counts: `{"extractor_bug": 13, "profile_gap": 275}`
- Pending facts: 0

## Claim Status

| Claim | Status | Rationale |
| --- | --- | --- |
| `C1` Runtime NASA ATMONTO profile feasibility | `supported_by_pilot` | The pilot generated the schema catalog, ATCSCC schema slice, and validated candidate-fact artifact. This remains a schema-engineering claim. |
| `C2` Schema-slice constraint benefit | `supported` | S2 schema violation rate is at least 10 percentage points lower than S1; gold-supported fact suppression still needs reviewed gold if unavailable. |
| `C3` Validator/repair benefit | `supported` | S3 meets the repair-success threshold and preserves semantic correctness. |
| `C4` Rejection analysis utility | `supported` | All 288 rejections have final property-level action labels: {"extractor_bug": 13, "profile_gap": 275}. |

## Hypothesis Status

| Hypothesis | Status | Falsification criterion |
| --- | --- | --- |
| `H1` Schema guidance reduces structural drift | `supported` | Falsified if S2 does not reduce schema violation rate versus S1 by at least 10 percentage points, or if the reduction only comes from suppressing more than 25 percent of gold-supported facts. |
| `H2` Validator/repair improves valid yield | `supported` | Falsified if S3 repair success is below 15 percent of initially invalid facts, or if S3 manual semantic correctness is more than 5 percentage points lower than S2. |
| `H3` Ontology constraints improve precision more than they harm recall | `supported` | Falsified if S3 precision does not exceed S1, or if S3 F1 is lower than S1 by more than 5 percentage points. |
| `H4` Rejection triage produces actionable engineering decisions | `supported` | Falsified if more than 20 percent of rejected facts remain manual-review-only after review, or if profile extensions cannot be tied to source evidence and NASA ATMONTO terms. |

## Completion Audit

- Overall status: `formal_experiment_complete`
- Blocking requirements: `[]`

| Requirement | Status | Evidence |
| --- | --- | --- |
| `R0` Position the current NASA ATMONTO loop as pilot / feasibility evidence, not a completed formal experiment. | `satisfied` | docs/experiment_protocol.md contains pilot/feasibility boundary and bronze-until-reviewed language. |
| `R1` Sample 80-120 ATCSCC advisories for the formal gold set. | `satisfied` | sample_size=100; manifest=data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json |
| `R2` Freeze reviewed gold annotations before semantic scoring. | `satisfied` | gold_source=frozen_reviewed_gold; template_reviewed=100; template_pending=0 |
| `R3` Define the four systems: rule-only, LLM-only, schema slice, schema slice plus validator/repair. | `satisfied` | systems=S0_rule_only,S1_llm_only,S2_llm_schema_slice,S3_llm_schema_slice_validator_repair |
| `R4` Run all four systems on the identical sampled records. | `satisfied` | {"S0_rule_only": true, "S1_llm_only": true, "S2_llm_schema_slice": true, "S3_llm_schema_slice_validator_repair": true} |
| `R5` Define JSON, schema, semantic, repair, and manual-correctness metrics. | `satisfied` | docs/experiment_protocol.md and reports/stages/nasa_atmonto_formal_experiment_scoring.json |
| `R6` Report JSON adherence, schema violation rate, precision/recall/F1, repair success, and manual semantic correctness. | `satisfied` | all_system_outputs=True; all_semantic_metrics_available=True |
| `R7` Account for all 288 pilot rejections in property-level error analysis. | `satisfied` | rejected_fact_count=288; grouped_fact_count=288 |
| `R8` Finalize whether each rejection group is extractor bug, NASA ATMONTO profile gap, source ambiguity, or manual-review-only. | `satisfied` | {"extractor_bug": 13, "profile_gap": 275} |
| `R9` Assign supported, falsified, or inconclusive status to claims C1-C4 and hypotheses H1-H4. | `satisfied` | {"C1": "supported_by_pilot", "C2": "supported", "C3": "supported", "C4": "supported", "H1": "supported", "H2": "supported", "H3": "supported", "H4": "supported"} |
| `R10` Fix the protocol artifact with claims, hypotheses, baselines, metrics, and falsification criteria. | `satisfied` | docs/experiment_protocol.md |

## Missing Required Inputs


## Boundary

- Formal metrics are descriptive until all four systems have predictions and the frozen reviewed gold set is available.
