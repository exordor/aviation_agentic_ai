# NASA ATMONTO S5/S6 Independent Agentic Run

## Boundary

This is an independent, deterministic, artifact-driven S5/S6 run over source-derived S0 candidates. It is independent from S4 output and scored against reviewed gold, but it is not a live LLM multi-agent generation run.

## Summary

- Status: `s5_s6_independent_agentic_run_scored`
- Input records: 100
- Extractor input system: `S0_rule_only`
- Independent from S4: `True`
- Live LLM run: `False`
- S5 accepted facts: 567
- S6 refined facts: 545
- Quarantined facts: 22
- Prediction output: `data/experiments/nasa_atmonto/formal/s5_s6_independent_agentic_predictions.jsonl`
- Run metadata: `data/experiments/nasa_atmonto/formal/s5_s6_independent_agentic_run_metadata.json`

## Agent Roles

| Agent | Input | Operation | Output |
| --- | --- | --- | --- |
| `extractor` | formal ATCSCC source records plus S0 source-derived candidates | start from source-derived candidate facts without reading S4 output | candidate fact payloads |
| `validator` | candidate fact payloads and NASA ATMONTO ATCSCC schema slice | rerun schema, datatype, range, and evidence validation | S5 validator-accepted facts and validator rejections |
| `critic` | S5 accepted facts, CQ manifest, source text, and profile heuristics | flag duplicate facts, unsupported evidence, and text-artifact NAS elements | critic quarantine reasons |
| `refiner` | critic decisions | drop quarantined facts and annotate accepted facts with CQ/module routes | S6 refined facts for scoring |

## Semantic Metrics

| Layer | Predicted | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S0 reported | 566 | 462 | 104 | 181 | 0.8163 | 0.7185 | 0.7643 |
| S5 validator accepted | 566 | 462 | 104 | 181 | 0.8163 | 0.7185 | 0.7643 |
| S6 critic refined | 545 | 462 | 83 | 181 | 0.8477 | 0.7185 | 0.7778 |

- Delta S6 minus S5: `{'predicted_fact_count': -21, 'true_positive_count': 0, 'precision': 0.0314, 'recall': 0.0, 'f1': 0.0135}`
- Delta S6 minus S0: `{'predicted_fact_count': -21, 'true_positive_count': 0, 'precision': 0.0314, 'recall': 0.0, 'f1': 0.0135}`

## Critic / Refiner Quarantine

| Reason | Fact count |
| --- | ---: |
| `duplicate_canonical_fact` | 1 |
| `text_artifact_controlled_element` | 21 |

### Examples

- `2026-05-19:032` `controlledNASelement` `fact-8512415585cd427c`: text_artifact_controlled_element
- `2026-05-19:032` `controlledNASelement` `fact-fa412a843d8bd200`: text_artifact_controlled_element
- `2026-05-19:032` `controlledNASelement` `fact-1925abbdac300f9f`: text_artifact_controlled_element
- `2026-05-19:032` `controlledNASelement` `fact-9460e6cc9c541109`: duplicate_canonical_fact
- `2026-05-19:032` `controlledNASelement` `fact-d79659753d38bd62`: text_artifact_controlled_element
- `2026-05-15:063` `controlledNASelement` `fact-b670ee084565cf3d`: text_artifact_controlled_element
- `2026-05-15:063` `controlledNASelement` `fact-ff0d97c756b59437`: text_artifact_controlled_element
- `2026-05-15:063` `controlledNASelement` `fact-9937cf1feef86807`: text_artifact_controlled_element
- `2026-05-15:063` `controlledNASelement` `fact-623b32490b71dea4`: text_artifact_controlled_element
- `2026-05-18:069` `controlledNASelement` `fact-020653628356973c`: text_artifact_controlled_element

## CQ / Module Routing

| Module | Fact count |
| --- | ---: |
| `deterministic_core` | 394 |
| `graph_query` | 118 |
| `validator_evidence` | 33 |

- Unmapped facts: 0

## SOTA Interpretation

- Satisfied: The artifact contract now drives an independent scored S5/S6 pass that starts from source-derived S0 candidates rather than S4 output.
- Remaining gap: A future upgrade should replace the deterministic extractor with live LLM extractor, validator, critic, and refiner agents under the same contract.
- Claim use: Use this as evidence for an independent artifact-driven loop; do not cite it as a live autonomous LLM multi-agent extraction result.
