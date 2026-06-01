# NASA ATMONTO Gold Review batch_01

- Samples: `ATCSCC-GOLD-001` to `ATCSCC-GOLD-010`
- Records: 10
- Candidate clusters: 201

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-001 / 2026-05-19:032

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=32
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. EFFECTIVE TIME: 191322-191630 SIGNATURE: 26/05/19 13:22 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-028f0c829d3c8bbc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `adds route` | L454 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDS L454 |
| `cand-07f1cc7967488d7d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `advises route closure` | L454 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-092d47690b54cb8b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THAT | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-0a21577a5ac29628` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names constrained facility` | ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-0d64d9e19b33673a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective time` | 191322-191630 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191322-191630 |
| `cand-2a5e39256de37832` | `S0_rule_only` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | _RQD |
| `cand-2eb7db50e5f7e305` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ARE | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-301f33e2d2f289d2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `cause stated in advisory` | severe turbulence | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-3b57350acc52b219` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports event time window` | 19/1200 - 19/1600 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/1200 - 19/1600 |
| `cand-3e8ed1851904958f` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T16:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191322-191630 |
| `cand-5452139e1194c658` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADVZY | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-580069f2df1cb6f9` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:AR8 | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-64f6e977c8b8b2b8` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T13:22:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191322-191630 |
| `cand-6db320888d86cf81` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:L454 | `{"repaired_accepted": 2}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-6eb16a7e8c55784b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `replaces advisory` | 027 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY REPLACES ADVZY 027 |
| `cand-7ca7a8175b5dcbba` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-8dfa6e571ced77bf` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T13:22:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 13:22 |
| `cand-9eb97d2e1da20337` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory title` | DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-ac9d2adf8b490464` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 32, "atm:controlledNASelement": "nas:Airport", "atm:implementationStatus": "RQD", "atm:initiativeComments": "EVENT TIME: 19/1200 - 19/... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-ace3995078cb8d5d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `advises route closure` | AR8 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-b0741a17a8907a39` | `S1_llm_only` | `freeform_or_unmapped_fact` | `encouraged action` | file alternate routes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. |
| `cand-c03e0e96bf714bf5` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADDS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-c1de08278625081b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:L452 | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-cb50e577a436ebf3` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-dbcc2bf733c1011c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `advises route closure` | L452 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-ec3d65f234308d7e` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 32 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD |

## ATCSCC-GOLD-002 / 2026-05-15:063

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=63
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 20

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 15/1918 - 16/0000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 151918-160030 SIGNATURE: 26/05/15 19:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0fc5ccead1be737c` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `initiativeComments` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-161d19bb2457224a` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-16cea73047f944c1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `have_maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-2a48e7bbcc59050a` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:18:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-3672d79202199bb9` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T19:18:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 19:18 |
| `cand-4b0313b23f63448b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-5297ec1c5d2761c1` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS", "value": 63}], "atm:controlledNASelement": [{"evi... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-62104fae3fc48981` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-765670f6e4fa2213` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T00:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-8e914b000fb4c268` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_time_span` | 15/1918 - 16/0000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 15/1918 - 16/0000 |
| `cand-8ff69121d548c758` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect` | arrival delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT |
| `cand-a950f4bd345702d7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect` | airborne holding into San Diego Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT |
| `cand-c9ba0ce9ac4c78b7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_due_to` | compacted demand | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-cbe6cb9e8f529674` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-d7d6b2834e8708ad` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 63 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-e2a1b014664055e9` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DIEGO | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-e33d82cdf5f8ea54` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-e34afc5641d4e0d1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces` | SAN airport arrival delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-e517d0ce120e6c3e` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 63 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-f09f8f65ffee2a81` | `S1_llm_only` | `freeform_or_unmapped_fact` | `will_follow_if_necessary` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |

## ATCSCC-GOLD-003 / 2026-05-18:069

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=69
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 18/1545 - 18/2000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 181545-182030 SIGNATURE: 26/05/18 15:45 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0e181c118f2336ff` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'runs_from'}` | {'type': 'timestamp', 'value': '18/1545'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1545 - 18/2000 |
| `cand-120cdf0b1c721a94` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-1e26b75fad279cbf` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-34509fba5cff2a43` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'runs_to'}` | {'type': 'timestamp', 'value': '18/2000'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1545 - 18/2000 |
| `cand-352fa3f8ffa176d7` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 69, "atm:controlledNASelement": [{"label": "LAS Vegas Airport", "type": "nas:Airport"}], "atm:impactingCondition": "volume"} | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. |
| `cand-36ca8aa6177e203d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'promises_follow_up_updates_if_necessary'}` | {'type': 'update_notice', 'value': 'updates'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-38785d11ab0ada24` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T15:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181545-182030 |
| `cand-4760f2ad6956d861` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T20:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181545-182030 |
| `cand-4ffa09fa1d5d46e6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'starts_at'}` | {'type': 'timestamp', 'value': '181545'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181545-182030 |
| `cand-528e728421552d1b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'can_expect_arrival_delays_or_airborne_holding'}` | {'type': 'delay_duration', 'value': 'up to 30 minutes'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-62203ca7bdf174b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_airport_arrival_delays'}` | {'type': 'airport', 'value': 'Las Vegas Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-70163bcbdf393132` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-7716781deb55b778` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-8fa6b710bd1d5da8` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 69 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-94d9fa191e3139b0` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:VEGAS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-95d49a54ce077cd4` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T15:45:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 15:45 |
| `cand-a6374f633815578f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'ends_at'}` | {'type': 'timestamp', 'value': '182030'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181545-182030 |
| `cand-ae202e6c578cf9f7` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-dff8aeaf815f6117` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'caused_by'}` | {'type': 'demand_condition', 'value': 'compacted demand'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |

## ATCSCC-GOLD-004 / 2026-05-14:059

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=59
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 22

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ EFFECTIVE TIME: 141554-150100 SIGNATURE: 26/05/14 15:54 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00c0511c5c79dd86` | `S1_llm_only` | `freeform_or_unmapped_fact` | `have_reported_maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OF UP TO 30 MINUTES |
| `cand-0d780d499932424c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_constrained_facility_area` | ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-1200498a6b820544` | `S1_llm_only` | `freeform_or_unmapped_fact` | `include_airports` | CDW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-16c387993394ef3f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `promises_updates` | will follow if necessary | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-16efed923f2aaa45` | `S1_llm_only` | `freeform_or_unmapped_fact` | `include_airports` | MMU | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-1e4fba32b4173686` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:AND | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-372b3374dd5a388b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect_arrival_delays_and_airborne_holding_into` | Newark and Newark satellite airports | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS |
| `cand-5c98dfe854c0775f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `include_airports` | TEB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-5f0a41c1b63f8abb` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T15:54:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 15:54 |
| `cand-688b63b83e7e709a` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-74943c40174a0219` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:54:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141554-150100 |
| `cand-81e4e79f13cc9122` | `S1_llm_only` | `freeform_or_unmapped_fact` | `include_airports` | LDJ | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-81ef1036e4ef1a27` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 59, "atm:effectiveEndTime": "2026-05-15T01:00:00Z", "atm:effectiveStartTime": "2026-05-14T15:54:00Z", "atm:initiativeComments": "ZNY U... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-8cd2f614737f070c` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T01:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141554-150100 |
| `cand-9a29660c620c0051` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-a7429d149fe9768e` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-ce6c81d4edf89109` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_event_time_window` | 14/1700 - 15/0100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/1700 - 15/0100 |
| `cand-d3aa06f8e2750561` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_event_title` | EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-dad475c94e2a63a1` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 59 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-ed947243711b49a3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_due_to` | compacted demand | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-eeaf7c3ed2af20f8` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-f736715cc2651ce1` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 59, "atm:controlledNASelement": {"@type": "nas:Airport", "evidence_text": "EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS"}, "atm:effective... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWA... |

## ATCSCC-GOLD-005 / 2026-05-19:059

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=59
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI MESSAGE: EVENT TIME: 19/1645 - 20/0200 CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 191638-200230 SIGNATURE: 26/05/19 16:38 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-15984c6fdfc39bac` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |
| `cand-2362f4bf93684b17` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T16:38:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 16:38 |
| `cand-2798d2bfdf3fec6b` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-19T16:38:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 16:38 |
| `cand-2a8035c83813c98b` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `advisoryNumber` | 59 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-3c222d94dc466e4b` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'IAH', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-3e06585bdc31c50b` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `implementationStatus` | FYI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-440dfec6c3737b81` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies constrained facilities'}` | {'label': 'ZHU'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-480afcfebd3554b8` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |
| `cand-5554272cff507ff2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'gives operational instruction'}` | {'label': 'users should fuel accordingly'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-66f3229b06234ca5` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191638-200230 |
| `cand-8327071940ea7414` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is implementing'}` | {'label': 'CDRS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-8cb5c6e57baab0f9` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `reRouteReason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-8e31ab13cc588a4c` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-ac95c2adb307c435` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 59 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-b0b0983cc362175b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T16:38:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191638-200230 |
| `cand-bb1869596e10d90c` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `reRouteType` | CDR | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-c058fc23d018050e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states event time'}` | {'label': '19/1645 - 20/0200'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/1645 - 20/0200 |
| `cand-c464cc07c2eb3fcb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states effective time'}` | {'label': '191638-200230'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191638-200230 |
| `cand-d16b6af5bfe69e8d` | `S2_llm_schema_slice` | `schema_shaped_object` | `advisoryNumber` | 59 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-d519682f33ab6f69` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reason stated as'}` | {'label': 'weather'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-d7d7d49b9699a91d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'mentions locations'}` | {'label': 'IAH HOU'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-e3bdf262b43e622a` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'HOU', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-f698d5950fd5dfab` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `type` | atm:ReRouteTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |

## ATCSCC-GOLD-006 / 2026-05-19:144

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=144
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED MESSAGE: EVENT TIME: 19/2230 - 20/0300 CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. EFFECTIVE TIME: 192220-200330 SIGNATURE: 26/05/19 22:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-050263318f4f550f` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED", "value": 144}], "atm:controlledNASel... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-07fcb2a51ff11716` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T03:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-23192b28e9c65220` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DROP | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-40fbcd9674194d16` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'causes flight plan drop times to be generated from'}` | {'class': 'traffic_management_time', 'label': 'EDCT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-43633790f4569b9a` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:HAS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-510ff876261f5354` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 144 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-532c30b99c554ecc` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T22:20:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-878c9beec21df694` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PLAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-8941d7b4003417d3` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:TIMES | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-8b31cbaabee84c85` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'set to duration'}` | {'class': 'time_duration', 'label': '180 minutes'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-a511ca8108699493` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has implemented'}` | {'class': 'operational_procedure', 'label': 'extended flight plan drop times'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-a54d42868f9a3c8b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-bc6b2c4948943b66` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 144 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-da01bad269e245b8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'triggered by condition'}` | {'class': 'unspecified_cause', 'label': 'XXX'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. |
| `cand-de845640deefb908` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces'}` | {'class': 'operational_action', 'label': 'extended flight plan drop times implemented'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-e60e33c3e6d9801e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'are generated from'}` | {'class': 'traffic_management_time', 'label': 'EDCT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-fe10f1cc9f81bc7b` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T22:20:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 22:20 |

## ATCSCC-GOLD-007 / 2026-05-16:051

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=51
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 14

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI MESSAGE: EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 161818-162330 SIGNATURE: 26/05/16 18:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0bb19b62a67f50b0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `instruction` | fuel accordingly | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-203778762dc94ff2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_event_time_window` | 16/1818 - 16/2300 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1818 - 16/2300 |
| `cand-332f96f27ff8beef` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T18:18:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 18:18 |
| `cand-4e533db99ede08c6` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |
| `cand-5ea2f433986c589d` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |
| `cand-86169b87825035f0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-89044d479fabab7a` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:implementationStatus": [{"evidence_text": "ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI", "value": "FYI"}], "atm:reRouteReason": [{"evidence_text":... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-8d39633573e323b4` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T23:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-9e85829abb8551ed` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI", "value": 51}], "atm:controlledNASelement": [{"evidence_text": "... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI MESSAGE: EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 161818-162330... |
| `cand-a4c054e940f68da3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_effective_time_window` | 161818-162330 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161818-162330 |
| `cand-ad5916108a54e68f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_implementing` | CDRS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-be0993666da8b7e4` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 51 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-d0acc6f7a4bc1f7e` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T18:18:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-e9aba17d4f1dc6c9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_constrained_facility` | ZDV | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |

## ATCSCC-GOLD-008 / 2026-05-17:019

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=19
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES EFFECTIVE TIME: 171218-171645 SIGNATURE: 26/05/17 12:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-18cfe2c69d11db5b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SOUTH | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-25774fe6140d3cf3` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NE... |
| `cand-44cee5f9e12996db` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THE | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-48c632aa09af4381` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'MIA, PBI, FLL and their satellites'}` | {'label': 'example airports and satellites', 'value': 'MIA, PBI, FLL AND THEIR SATELLITES'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-4d0bcf4fa8e23773` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-5365462310e05848` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'up to 30 minutes'}` | {'label': 'delay duration', 'value': 'UP TO 30 MINUTES'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-5e2094d4220b3723` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T16:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171218-171645 |
| `cand-716969a52bb67bfe` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'arrival delays / airborne holding'}` | {'label': 'arrival delays and airborne holding', 'value': 'ARRIVAL DELAYS / AIRBORNE HOLDING'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-7c566bdc5eafd98a` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 19, "atm:controlledNASelement": [{"label": "MIA", "type": "nas:Airport"}, {"label": "PBI", "type": "nas:Airport"}, {"label": "FLL", "t... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-7c5f79007b5d369e` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-8e2e851c20720436` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'arrival delays / airborne holding'}` | {'label': 'arrival delays and airborne holding', 'value': 'ARRIVAL DELAYS / AIRBORNE HOLDING'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UP TO 30 MINUTES DUE TO THUNDERSTORMS |
| `cand-9b70f42975751291` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'if necessary'}` | {'label': 'future updates', 'value': 'UPDATES'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-b55d5f6183f6d4ac` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'arrival delays'}` | {'label': 'South Florida airports', 'value': 'SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| `cand-b80eea9e547c8542` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-c0cd6e01b50c5edf` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T12:18:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171218-171645 |
| `cand-cd716badd6aeb1e3` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 19 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| `cand-ec4eda07e331fc6d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T12:18:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 12:18 |
| `cand-f6e1e2a1a7da921f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'South Florida airports'}` | {'label': 'South Florida airports', 'value': 'THE SOUTH FLORIDA AIRPORTS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-fd0683497e7e907a` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |

## ATCSCC-GOLD-009 / 2026-05-20:040

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=40
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 21

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201400 PROBABILITY OF EXTENSION: MODERATE REMARKS: ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < REDDN4 KMCO KORL KSFB ZMA KDFW >JAWJA MGMRY SARKK YUYUN < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA MGMRY SARKK PUDJE < REDDN4 TMI ID: RRDCC504 EFFECTIVE TIME: 201000-201400 SIGNAT...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-4e8ef2e6e542643a` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T10:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201400 |
| `cand-56342ef5c509eb89` | `S1_llm_only` | `freeform_or_unmapped_fact` | `facilities_included` | ['ZFW', 'ZHU', 'ZJX', 'ZMA', 'ZME', 'ZTL'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-583fe080fae3458a` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-7698910a7e51ebfb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | {'destination': 'KDAL', 'origin': 'KMCO', 'route': '>JAWJA MGMRY SARKK PUDJE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDAL >JAWJA MGMRY SARKK PUDJE |
| `cand-78628609b7be26fb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | {'destination': 'KDAL', 'origin': 'KMCO', 'route': '>JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS |
| `cand-8114f175c417ea48` | `S1_llm_only` | `freeform_or_unmapped_fact` | `probability_of_extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-8fd484f4da12a17b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_name` | FLORIDA_TO_TEXAS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: FLORIDA_TO_TEXAS |
| `cand-99b6b108fb6b7665` | `S1_llm_only` | `freeform_or_unmapped_fact` | `traffic_departures_to` | ['KDAL', 'KDFW'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-a5ea073bf0a1f5de` | `S1_llm_only` | `freeform_or_unmapped_fact` | `flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-afd30db2de4f3716` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_traffic` | ['KMCO', 'KORL', 'KSFB', 'ZMA'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-b2233e76ee8bb090` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time_window` | 201000-201400 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201000-201400 |
| `cand-b2a9eca7f0ae649d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_tmi_id` | RRDCC504 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC504 |
| `cand-b5bfee31e5283b78` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_area` | ZHU | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZHU |
| `cand-b71346e441867d09` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | {'destination': 'KDFW', 'origin': 'KMCO', 'route': '>JAWJA MGMRY SARKK YUYUN'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDFW >JAWJA MGMRY SARKK YUYUN |
| `cand-ba59518312d4db4e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | {'destination': 'KDFW', 'origin': 'KMCO', 'route': '>JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS |
| `cand-cbc5df0ac4e016d9` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 40 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-d055d0fd5785866d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T09:42:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 09:42 |
| `cand-dae2c1f9cec589a5` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T14:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201400 |
| `cand-dec998ca4d2499fa` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 40 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-f3ce9df94be46984` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-f56650288945d076` | `S1_llm_only` | `freeform_or_unmapped_fact` | `valid_time_window` | ETD 201000 TO 201400 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201400 |

## ATCSCC-GOLD-010 / 2026-05-20:053

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=53
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 20

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201700 PROBABILITY OF EXTENSION: MODERATE REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < REDDN4 TMI ID: RRDCC504 EFFECTIVE TIME: 201000-201700 SIGNATURE: 26/05/20 12:48 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| C...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-17b93edd1052a436` | `S1_llm_only` | `freeform_or_unmapped_fact` | `valid_from` | 201000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201700 |
| `cand-1be3efe7c8336007` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-23c53352b6f57970` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-2bcc09b1a3b59cfc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_named` | FLORIDA_TO_TEXAS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: FLORIDA_TO_TEXAS |
| `cand-34aecf002ba75f34` | `S1_llm_only` | `freeform_or_unmapped_fact` | `extends_end_time` | true | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-3de168c41e0e62b4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_area` | ZHU | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZHU |
| `cand-4e24661d6766d560` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-50858baaaea6c213` | `S1_llm_only` | `freeform_or_unmapped_fact` | `replaces_advisory` | ADVZY 042 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-7f3c773d2c3ac305` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time_range` | 201000-201700 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201000-201700 |
| `cand-888fa66ea6c40581` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 53 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-9f5fc1dcf334f02c` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T17:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201700 |
| `cand-a27e73c6dd2be516` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_traffic` | KMCO/KORL/KSFB/ZMA departures to KDAL/KDFW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-b7445d154db243e8` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T10:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201700 |
| `cand-bd16a9ac1a4c0dcc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `valid_to` | 201700 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201700 |
| `cand-cb10468ef23ec5db` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T12:48:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 12:48 |
| `cand-d14e0752a5482b1c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_facilities_included` | ZFW/ZHU/ZJX/ZMA/ZME/ZTL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-d2cb3a323297b1f4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-d88b9139a0eaecb0` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"id": "ZHU", "type": "nas:ARTCC"}, "atm:effectiveEndTime": "2026-05-20T17:00:00", "atm:effectiveStartTime": "2026-05-20T20:10:0... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-e3401695596846ad` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:extensionProbability": "MEDIUM", "atm:implementationStatus": "RQD", "atm:initiativeComments": "REPLACES ADVZY 042, EXTENDS END TIME.", "atm:reRouteReas... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201... |
| `cand-e84d45a1966885ef` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 53, "atm:effectiveEndTime": "2026-05-20T21:70:00Z", "atm:effectiveStartTime": "2026-05-20T20:10:00Z", "atm:extensionProbability": "MED... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
