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

| System | Output | JSON adherence | Candidate facts | Accepted | Rejected | Structural acceptance | Schema violation rate | Repair success | Semantic metrics |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `S0_rule_only` | `True` | 1.0 | 615 | 567 | 48 | 0.9219512195121952 | 0.07804878048780488 | n/a | pending:manual_gold_facts_missing |
| `S1_llm_only` | `True` | 1.0 | 1211 | 0 | 1211 | 0.0 | 1.0 | n/a | pending:manual_gold_facts_missing |
| `S2_llm_schema_slice` | `True` | 1.0 | 708 | 361 | 347 | 0.5098870056497176 | 0.4901129943502825 | n/a | pending:manual_gold_facts_missing |
| `S3_llm_schema_slice_validator_repair` | `True` | 1.0 | 396 | 286 | 110 | 0.7222222222222222 | 0.2777777777777778 | 0.7222222222222222 | pending:manual_gold_facts_missing |

## Rejection Adjudication

- Property-level complete: `True`
- Decision counts: `{"extractor_bug": 13, "profile_gap": 275}`
- Pending facts: 0

## Claim Status

| Claim | Status | Rationale |
| --- | --- | --- |
| `C1` Runtime NASA ATMONTO profile feasibility | `supported_by_pilot` | The pilot generated the schema catalog, ATCSCC schema slice, and validated candidate-fact artifact. This remains a schema-engineering claim. |
| `C2` Schema-slice constraint benefit | `supported_structural_only` | S2 schema violation rate is at least 10 percentage points lower than S1; gold-supported fact suppression still needs reviewed gold if unavailable. |
| `C3` Validator/repair benefit | `pending_manual_gold` | Structural repair can be inspected, but semantic preservation requires reviewed gold. |
| `C4` Rejection analysis utility | `supported` | All 288 rejections have final property-level action labels: {"extractor_bug": 13, "profile_gap": 275}. |

## Hypothesis Status

| Hypothesis | Status | Falsification criterion |
| --- | --- | --- |
| `H1` Schema guidance reduces structural drift | `supported_structural_only` | Falsified if S2 does not reduce schema violation rate versus S1 by at least 10 percentage points, or if the reduction only comes from suppressing more than 25 percent of gold-supported facts. |
| `H2` Validator/repair improves valid yield | `pending_manual_gold` | Falsified if S3 repair success is below 15 percent of initially invalid facts, or if S3 manual semantic correctness is more than 5 percentage points lower than S2. |
| `H3` Ontology constraints improve precision more than they harm recall | `pending_manual_gold` | Falsified if S3 precision does not exceed S1, or if S3 F1 is lower than S1 by more than 5 percentage points. |
| `H4` Rejection triage produces actionable engineering decisions | `supported` | Falsified if more than 20 percent of rejected facts remain manual-review-only after review, or if profile extensions cannot be tied to source evidence and NASA ATMONTO terms. |

## Completion Audit

- Overall status: `formal_experiment_pending`
- Blocking requirements: `["R2", "R6", "R9"]`

| Requirement | Status | Evidence |
| --- | --- | --- |
| `R0` Position the current NASA ATMONTO loop as pilot / feasibility evidence, not a completed formal experiment. | `satisfied` | docs/experiment_protocol.md contains pilot/feasibility boundary and bronze-until-reviewed language. |
| `R1` Sample 80-120 ATCSCC advisories for the formal gold set. | `satisfied` | sample_size=100; manifest=data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json |
| `R2` Freeze reviewed gold annotations before semantic scoring. | `pending_manual_input` | gold_source=frozen_reviewed_gold_missing; template_reviewed=0; template_pending=100 |
| `R3` Define the four systems: rule-only, LLM-only, schema slice, schema slice plus validator/repair. | `satisfied` | systems=S0_rule_only,S1_llm_only,S2_llm_schema_slice,S3_llm_schema_slice_validator_repair |
| `R4` Run all four systems on the identical sampled records. | `satisfied` | {"S0_rule_only": true, "S1_llm_only": true, "S2_llm_schema_slice": true, "S3_llm_schema_slice_validator_repair": true} |
| `R5` Define JSON, schema, semantic, repair, and manual-correctness metrics. | `satisfied` | docs/experiment_protocol.md and reports/stages/nasa_atmonto_formal_experiment_scoring.json |
| `R6` Report JSON adherence, schema violation rate, precision/recall/F1, repair success, and manual semantic correctness. | `pending_scoring` | all_system_outputs=True; all_semantic_metrics_available=False |
| `R7` Account for all 288 pilot rejections in property-level error analysis. | `satisfied` | rejected_fact_count=288; grouped_fact_count=288 |
| `R8` Finalize whether each rejection group is extractor bug, NASA ATMONTO profile gap, source ambiguity, or manual-review-only. | `satisfied` | {"extractor_bug": 13, "profile_gap": 275} |
| `R9` Assign supported, falsified, or inconclusive status to claims C1-C4 and hypotheses H1-H4. | `pending_scoring` | {"C1": "supported_by_pilot", "C2": "supported_structural_only", "C3": "pending_manual_gold", "C4": "supported", "H1": "supported_structural_only", "H2": "pending_manual_gold", "H3": "pending_manual_gold", "H4": "supported"} |
| `R10` Fix the protocol artifact with claims, hypotheses, baselines, metrics, and falsification criteria. | `satisfied` | docs/experiment_protocol.md |

## Missing Required Inputs

- frozen reviewed gold set at data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl
- completed manual gold annotations for 100 sampled advisories
- manual semantic metrics require reviewed gold facts

## Boundary

- Formal metrics are descriptive until all four systems have predictions and the frozen reviewed gold set is available.
