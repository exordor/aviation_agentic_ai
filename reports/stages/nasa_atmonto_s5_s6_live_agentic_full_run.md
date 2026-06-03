# NASA ATMONTO S5/S6 Live Agentic Full Run

## Boundary

This is a live multi-agent LLM run over 100 reviewed ATCSCC samples. It exercises extractor, deterministic validator, live critic, and live refiner roles under hard ontology/evidence gates. It supports method-level evaluation of event-centric semantic KG extraction, but it must not be cited as operational decision support.

## Summary

- Status: `s5_s6_live_agentic_full_run_scored`
- Input records: 100
- Independent from S4: `True`
- Live LLM run: `True`
- Provider/model: `openai` / `gpt-5.4-mini`
- Prompt version: `atcscc_s5_s6_live_agentic_pilot_v2`
- Run scope: `full_run`
- S5 accepted facts: 535
- S6 refined facts: 485
- Quarantined facts: 50
- Prediction output: `data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_full_run_predictions.jsonl`
- Run metadata: `data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_full_run_metadata.json`

## Agent Roles

| Agent | Input | Operation | Output |
| --- | --- | --- | --- |
| `extractor` | ATCSCC source text plus ATMONTO ATCSCC profile menu | live LLM schema-constrained fact proposal | candidate flat KG facts with copied evidence spans |
| `validator` | extractor facts, source text, and schema slice | deterministic schema, datatype/range, and evidence validation | S5 validator-accepted facts and validator rejections |
| `critic` | S5 facts, CQ routes, validator rejections, and source text | live LLM critique with deterministic duplicate/text-artifact safeguards | drop decisions and quarantine reasons |
| `refiner` | critic-filtered S5 facts | live LLM final payload rewrite under no-new-facts safety gate | S6 facts retained after final deterministic validation |

## Quality Counters

- Failed records: 0
- Failure type counts: `{}`
- Extractor JSON adherence: 100
- Final schema-valid records: 96
- Refiner fallback count: 96
- Agent call counts: `{'extractor': 100, 'validator': 100, 'critic': 97, 'refiner': 96}`

## Semantic Metrics

| Layer | Predicted | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S5 validator accepted | 535 | 270 | 265 | 373 | 0.5047 | 0.4199 | 0.4584 |
| S6 live refined | 485 | 257 | 228 | 386 | 0.5299 | 0.3997 | 0.4557 |
- Delta S6 minus S5: `{'predicted_fact_count': -50, 'true_positive_count': -13, 'precision': 0.0252, 'recall': -0.0202, 'f1': -0.0027}`

## Critic / Refiner Quarantine

| Reason | Fact count |
| --- | ---: |
| `live_critic:Boilerplate/text artifact: the evidence is an advisory message line for the CTL element, but it does not explicitly support the object-property claim that the program includes airport BNA.` | 1 |
| `live_critic:Copied evidence only supports the bulletin title; the extra gloss about ash clouds over Guatemala is not present in the source text.` | 1 |
| `live_critic:Duplicate boilerplate/title text already captured in the advisory header; not a distinct supported fact.` | 1 |
| `live_critic:Duplicate initiativeComments fact for the same subject/predicate; value is a broader header-style comment and is superseded by the more specific evidence in fact-06.` | 1 |
| `live_critic:Duplicate of fact-06 with the same evidence text and essentially the same extracted comment content.` | 1 |
| `live_critic:Duplicate of fact-07 with overlapping evidence for the same controlled NAS element; keep only one.` | 1 |
| `live_critic:Duplicate of fact-08 with weaker evidence; same departureScope assertion repeated.` | 1 |
| `live_critic:Duplicate/less supported comment fact; it is just the title text and is subsumed by the more specific evidence-backed initiative comment.` | 1 |
| `live_critic:Evidence omits the leading 'COMMENTS:' token, so the extracted value should not include it if strict span fidelity is required.` | 1 |
| `live_critic:Evidence only supports a control element value of ORD; the object class/value pairing appears over-specific relative to the copied text, and this fact was rejected elsewhere for subject-class issues.` | 1 |
| `live_critic:Evidence says 'IMPACTING CONDITION: WEATHER / THUNDERSTORMS' but the accepted value is normalized to 'weather', which is only partially supported by the copied evidence.` | 1 |
| `live_critic:Evidence shows a time range; the extracted end value `2026-05-14T14:00:00Z` is not supported by the copied text.` | 1 |
| `live_critic:Evidence shows a time range; the extracted start time 18:40Z is not directly supported by the copied text.` | 1 |
| `live_critic:Evidence shows a time range; the extracted start value `2026-05-14T00:00:00Z` is not supported by the copied text.` | 1 |
| `live_critic:Evidence supports effective time, but the parsed value is slightly normalized; not a duplicate or unsupported fact.` | 2 |
| `live_critic:Evidence supports the initiative comment being 'STAFFING'; 'STAFFING COMMENTS:' appears to be a label/artifact and not the fact value.` | 1 |
| `live_critic:Evidence text ends with a boilerplate label sequence; the value 'GS CNX' is directly supported earlier in the same span, so the copied evidence also contains trailing artifact text.` | 1 |
| `live_critic:Evidence text truncates with 'MODIFICATIONS: END TIME ' in the cq route snippet, but the accepted fact asserts the full ending 'END TIME EXTENDED.'; this support is from the full source text, so the cq route evidence alone is incomplete for that exact value.` | 1 |
| `live_critic:Not duplicate; supported by copied evidence.` | 2 |
| `live_critic:Not supported by copied evidence: 'CTL ELEMENT: SFO ELEMENT TYPE: APT' supports a control element, not departureScope.` | 1 |
| `live_critic:Not supported by copied evidence: 'GROUND STOP PERIOD' supports the period, not flightInclusionSpec. It also looks like a source-span artifact rather than an explicit inclusion specification.` | 1 |
| `live_critic:Not supported by the copied evidence as a clean fact value; it appears to be a truncated page/header fragment rather than a complete advisory comment.` | 1 |
| `live_critic:Source text supports a GroundStopTMI scope object, but the fact is typed as departureScope with an AirportSpec object; the copied evidence only shows CTL ELEMENT and does not directly support this broader object encoding as stated.` | 1 |
| `live_critic:Supported by advisory line; no issue.` | 1 |
| `live_critic:Supported by effective time line; no issue.` | 2 |
| `live_critic:Supported by probability of extension line; no issue.` | 1 |
| `live_critic:Supported by signature timestamp; no issue.` | 1 |
| `live_critic:Supported by the effective time range, though the exact extraction appears normalized rather than copied verbatim.` | 1 |
| `live_critic:Supported by the evidence text, but the normalized value appears inconsistent with the source span. 'EFFECTIVE TIME: 170000-170000' is a same-day time range, not clearly the end time '2026-05-17T17:00:00Z'.` | 1 |
| `live_critic:Supported by the evidence text, but the normalized value appears inconsistent with the source span. 'EFFECTIVE TIME: 170000-170000' is a same-day time range, not clearly the start time '2026-05-17T00:00:00Z'.` | 1 |
| `live_critic:The copied evidence mentions 'CTL ELEMENT: PHL' and 'ELEMENT TYPE: APT'; the asserted departureScope object adds a specific airport interpretation that is not directly stated in the evidence.` | 1 |
| `live_critic:The evidence is a page/title line, but the normalized comment value adds paraphrased meaning not explicitly copied from the source.` | 1 |
| `live_critic:The evidence supports controlled NAS element BNA, but the extracted predicate/value 'departureScope' is not directly supported by the span and appears misclassified.` | 1 |
| `live_critic:The extracted object value 'BNA ELEMENT TYPE: APT ADL TIME: 2129Z' is a copied text fragment combining multiple fields, not a supported object value.` | 1 |
| `live_critic:Value is a normalized paraphrase of the evidence; acceptable as supported.` | 3 |
| `live_critic_drop` | 30 |

### Examples

- `2026-05-15:063` `initiativeComments` `S5_live_llm_extractor_agent:ATCSCC-GOLD-002:fact-05-cd8a70068b8e`: live_critic:Duplicate initiativeComments fact for the same subject/predicate; value is a broader header-style comment and is superseded by the more specific evidence in fact-06., live_critic_drop
- `2026-05-18:069` `initiativeComments` `S5_live_llm_extractor_agent:ATCSCC-GOLD-003:fact-05-764666d3a0c7`: live_critic:Duplicate/less supported comment fact; it is just the title text and is subsumed by the more specific evidence-backed initiative comment., live_critic_drop
- `2026-05-14:059` `initiativeComments` `S5_live_llm_extractor_agent:ATCSCC-GOLD-004:fact-05-5d488d3cc3bc`: live_critic_drop
- `2026-05-20:078` `initiativeComments` `S5_live_llm_extractor_agent:ATCSCC-GOLD-016:fact-09-bcd0fbaa0b66`: live_critic:Evidence text truncates with 'MODIFICATIONS: END TIME ' in the cq route snippet, but the accepted fact asserts the full ending 'END TIME EXTENDED.'; this support is from the full source text, so the cq route evidence alone is incomplete for that exact value.
- `2026-05-19:079` `includesAirport` `S5_live_llm_extractor_agent:ATCSCC-GOLD-017:fact-07-a9e9f9d4f2d3`: live_critic:Boilerplate/text artifact: the evidence is an advisory message line for the CTL element, but it does not explicitly support the object-property claim that the program includes airport BNA., live_critic_drop
- `2026-05-19:074` `effectiveStartTime` `S5_live_llm_extractor_agent:ATCSCC-GOLD-018:fact-03-5e49afe8abff`: live_critic:Evidence shows a time range; the extracted start time 18:40Z is not directly supported by the copied text.
- `2026-05-19:074` `effectiveEndTime` `S5_live_llm_extractor_agent:ATCSCC-GOLD-018:fact-04-883c811a3477`: live_critic:Supported by the effective time range, though the exact extraction appears normalized rather than copied verbatim.
- `2026-05-15:067` `impactingConditionMessage` `S5_live_llm_extractor_agent:ATCSCC-GOLD-019:fact-06-3584647d9169`: live_critic:Not duplicate; supported by copied evidence.
- `2026-05-15:067` `initiativeComments` `S5_live_llm_extractor_agent:ATCSCC-GOLD-019:fact-07-857eada47d7d`: live_critic:Not duplicate; supported by copied evidence.
- `2026-05-18:136` `initiativeComments` `S5_live_llm_extractor_agent:ATCSCC-GOLD-024:fact-06-b154a82cd784`: live_critic:Evidence supports the initiative comment being 'STAFFING'; 'STAFFING COMMENTS:' appears to be a label/artifact and not the fact value., live_critic_drop

## CQ / Module Routing

| Module | Fact count |
| --- | ---: |
| `deterministic_core` | 340 |
| `graph_query` | 82 |
| `unmapped_profile_fact` | 20 |
| `validator_evidence` | 43 |

| CQ | Fact count |
| --- | ---: |
| `CQ-A01` | 133 |
| `CQ-D01` | 89 |
| `CQ-D02` | 16 |
| `CQ-D03` | 251 |
| `CQ-E01` | 64 |
| `CQ-E02` | 88 |
| `CQ-E03` | 90 |
| `CQ-O01` | 172 |
| `CQ-O02` | 43 |
| `CQ-Q01` | 186 |

## SOTA Interpretation

- Satisfied: The project has a live LLM multi-agent S5/S6 run over the full reviewed ATCSCC input set, using the same ATMONTO profile, evidence gates, and semantic scoring layer as the deterministic controls.
- Remaining gap: A full SOTA claim still requires cost/latency accounting, answer-layer human review, and ideally transfer to a second event-centric domain.
- Claim use: Use this artifact as full-set live-agent evidence for the extraction method. Do not present it as operational readiness or as proof of general-domain transfer.
