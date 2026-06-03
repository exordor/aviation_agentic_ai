# NASA ATMONTO S5/S6 Live Agentic Pilot

## Boundary

This is a bounded live multi-agent LLM pilot over reviewed ATCSCC samples. It exercises extractor, deterministic validator, live critic, and live refiner roles under hard ontology/evidence gates. It is not a full 100-record formal run and must not be cited as operational decision support.

## Summary

- Status: `s5_s6_live_agentic_pilot_scored`
- Input records: 3
- Independent from S4: `True`
- Live LLM run: `True`
- Provider/model: `openai` / `gpt-5.4-mini`
- Prompt version: `atcscc_s5_s6_live_agentic_pilot_v2`
- S5 accepted facts: 16
- S6 refined facts: 15
- Quarantined facts: 1
- Prediction output: `data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_pilot_predictions.jsonl`
- Run metadata: `data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_pilot_run_metadata.json`

## Agent Roles

| Agent | Input | Operation | Output |
| --- | --- | --- | --- |
| `extractor` | ATCSCC source text plus ATMONTO ATCSCC profile menu | live LLM schema-constrained fact proposal | candidate flat KG facts with copied evidence spans |
| `validator` | extractor facts, source text, and schema slice | deterministic schema, datatype/range, and evidence validation | S5 validator-accepted facts and validator rejections |
| `critic` | S5 facts, CQ routes, validator rejections, and source text | live LLM critique with deterministic duplicate/text-artifact safeguards | drop decisions and quarantine reasons |
| `refiner` | critic-filtered S5 facts | live LLM final payload rewrite under no-new-facts safety gate | S6 facts retained after final deterministic validation |

## Quality Counters

- Extractor JSON adherence: 3
- Final schema-valid records: 3
- Refiner fallback count: 3
- Agent call counts: `{'extractor': 3, 'validator': 3, 'critic': 3, 'refiner': 3}`

## Semantic Metrics

| Layer | Predicted | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S5 validator accepted | 16 | 12 | 4 | 4 | 0.75 | 0.75 | 0.75 |
| S6 live refined | 15 | 12 | 3 | 4 | 0.8 | 0.75 | 0.7742 |
- Delta S6 minus S5: `{'predicted_fact_count': -1, 'true_positive_count': 0, 'precision': 0.05, 'recall': 0.0, 'f1': 0.0242}`

## Critic / Refiner Quarantine

| Reason | Fact count |
| --- | ---: |
| `live_critic:Duplicate/overlapping initiativeComments with fact-06; evidence span is just the title line and the extracted value is weaker than the fuller supported comment in fact-06.` | 1 |
| `live_critic_drop` | 1 |

### Examples

- `2026-05-18:069` `initiativeComments` `S5_live_llm_extractor_agent:ATCSCC-GOLD-003:fact-05-c0fa54364769`: live_critic:Duplicate/overlapping initiativeComments with fact-06; evidence span is just the title line and the extracted value is weaker than the fuller supported comment in fact-06., live_critic_drop

## CQ / Module Routing

| Module | Fact count |
| --- | ---: |
| `deterministic_core` | 12 |
| `graph_query` | 3 |

| CQ | Fact count |
| --- | ---: |
| `CQ-A01` | 3 |
| `CQ-D01` | 3 |
| `CQ-D03` | 9 |
| `CQ-E01` | 3 |
| `CQ-E02` | 3 |
| `CQ-E03` | 3 |
| `CQ-O01` | 6 |
| `CQ-Q01` | 6 |

## SOTA Interpretation

- Satisfied: The project now has a bounded live LLM multi-agent S5/S6 pilot that uses the same ATMONTO profile, evidence gates, and scoring layer as the deterministic run.
- Remaining gap: The live pilot is intentionally small. A full SOTA claim would require a full 100-record live run, cost/latency accounting, and human review of the answer layer.
- Claim use: Use this artifact as live-pilot evidence for the method design, not as proof that autonomous agents outperform the deterministic extractor.
