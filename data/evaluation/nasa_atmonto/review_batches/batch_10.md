# NASA ATMONTO Gold Review batch_10

- Samples: `ATCSCC-GOLD-091` to `ATCSCC-GOLD-100`
- Records: 10
- Candidate clusters: 197

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-091 / 2026-05-19:068

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=68
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAH ELEMENT TYPE: APT ADL TIME: 1742Z GROUND STOP PERIOD: 19/1732Z - 19/1845Z DEP FACILITIES INCLUDED: (Manual) ZTL ZHU PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 401 / 66 / 50 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: RWY-TAXI / DISABLED AIRCRAFT COMMENTS: DISABLED AC ON RWY 8R, USERS CAN EXPECT HOLDING DURING THIS TIME EFFECTIVE TIME: 191746-191945 SIGNATURE: 26/05/19 17:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1627cff4285a2b80` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAH | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAH |
| `cand-25f36248f3080d5a` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | DISABLED AC ON RWY 8R, USERS CAN EXPECT HOLDING DURING THIS TIME | `{"repaired_accepted": 1}` | `{}` | COMMENTS: DISABLED AC ON RWY 8R, USERS CAN EXPECT HOLDING DURING THIS TIME |
| `cand-2d1f6446974210e7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_ctl_element'}` | {'label': 'IAH'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAH |
| `cand-34802fc587169c24` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'located_on'}` | {'label': 'RWY 8R'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISABLED AC ON RWY 8R |
| `cand-48d4fe653c24784b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_effective_time'}` | {'label': '191746-191945'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191746-191945 |
| `cand-4ddf9a3a2af30646` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_ground_stop'}` | {'label': 'ground stop'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-5dbadca0e82b09ab` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_new_delays'}` | {'label': '401 / 66 / 50'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 401 / 66 / 50 |
| `cand-5f7e064f50c57bac` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-65612239cd02fa93` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_probability_of_extension'}` | {'label': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-687af757c44bd900` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_period'}` | {'label': '19/1732Z - 19/1845Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 19/1732Z - 19/1845Z |
| `cand-6fe8b259962d0d47` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-8036be5dd4b38844` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: IAH", "value": "urn:nas:Airport/IAH"}], "atm:extensionProbability": [{"evidence_text": "PROBABI... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-824ed204a602b69f` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 68 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-9277f2ce083acc9c` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T19:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191746-191945 |
| `cand-95af394fa2da31f0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_previous_delays'}` | {'label': '0 / 0 / 0'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-aa425f4d27a70349` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T17:47:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 17:47 |
| `cand-ac59707e27388311` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP", "value": 68}], "atm:controlledNASelement": [{"evidence_text"... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-cb5c6c274b546b28` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'gives_advisory_time'}` | {'label': '1742Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1742Z |
| `cand-e2a9d42cfa81517c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_controlled_airport'}` | {'label': 'IAH'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-f53d732bd1978f03` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T17:46:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191746-191945 |
| `cand-f6fb2a44fdca6eb5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names_control_facility'}` | {'label': 'ZHU'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-f76770d2a297f2a1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZTL ZHU'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZHU |
| `cand-f86eb13f62fcf969` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'can_expect'}` | {'label': 'holding during this time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT HOLDING DURING THIS TIME |
| `cand-fa96c99cd39b0edc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_impacting_condition'}` | {'label': 'RWY-TAXI / DISABLED AIRCRAFT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: RWY-TAXI / DISABLED AIRCRAFT |

## ATCSCC-GOLD-092 / 2026-05-15:075

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=75
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z CUMULATIVE PROGRAM PERIOD: 15/1700Z - 16/0359Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1042 / 180 / 55 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1875 / 273 / 99 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LOW CEILINGS COMMENTS: EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP EFFECTIVE TIME: 152115-152315 SIGNATURE: 26/05/15 21:16 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Vi...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01caef5b9fd17050` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-0ac0b50849d321e9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports new total maximum average delays'}` | {'label': '1875 / 273 / 99', 'type': 'delay_metrics'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1875 / 273 / 99 |
| `cand-17e1add735da0dc2` | `S2_llm_schema_slice` | `schema_shaped_object` | `advisoryNumber` | 75 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-419dca34a7f86a8f` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: BOS ELEMENT TYPE: APT", "value": "BOS"}], "atm:extensionProbability": [{"evidence_text": "PROBA... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-468596cb9f9aa7d0` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP |
| `cand-521d98cc942914bc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has effective time'}` | {'label': '152115-152315', 'type': 'effective_time_interval'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 152115-152315 |
| `cand-5a58230563d7c5ba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names impacting condition'}` | {'label': 'WEATHER / LOW CEILINGS', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-5fcffd728b2b740f` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / LOW CEILINGS | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-61a4d428a0e19e70` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T21:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152115-152315 |
| `cand-6ecf0c74c028901d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'gives probability of extension'}` | {'label': 'MEDIUM', 'type': 'extension_probability'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-705a194308cb5681` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names control element'}` | {'label': 'BOS', 'type': 'control_element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BOS |
| `cand-73a16a5251ff1b6c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'describes action as'}` | {'label': 'GROUND STOP', 'type': 'traffic_management_action'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP |
| `cand-74f9e939bf7f54c1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states expected follow-on action'}` | {'label': 'GDP TO BE REVISED FOLLOWING THE GROUND STOP', 'type': 'follow_on_action'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP |
| `cand-75deb998b2089c7f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has cumulative program period'}` | {'label': '15/1700Z - 16/0359Z', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 15/1700Z - 16/0359Z |
| `cand-772764549167a379` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T21:16:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 21:16 |
| `cand-87c1c8bf440b6439` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has ground stop period'}` | {'label': '15/2059Z - 15/2215Z', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 15/2059Z - 15/2215Z |
| `cand-a6e11bdab13ad19d` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T23:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152115-152315 |
| `cand-ccbfb35f30512e8a` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 75 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP |
| `cand-d105695d212ac280` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has advisory identifier'}` | {'label': 'ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP', 'type': 'advisory_identifier'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP |
| `cand-d65d940b68bca4a1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes departure facilities'}` | {'label': 'ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB', 'type': 'facility_list'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-dc97a14a0aa20e10` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports previous total maximum average delays'}` | {'label': '1042 / 180 / 55', 'type': 'delay_metrics'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1042 / 180 / 55 |
| `cand-e975e927ac3c95d1` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BOS | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BOS |
| `cand-fea52f54697764de` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-093 / 2026-05-18:060

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=60
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 18/1445 - 18/1800 CONSTRAINED FACILITIES: ZKC THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. EFFECTIVE TIME: 181444-181830 SIGNATURE: 26/05/18 14:44 FAA.gov Home \| Privacy Policy \| Web Policies &...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05e053f3c69ffba0` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181444-181830 |
| `cand-0691897a927e8184` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'will_close_at_end_of'}` | {'label': 'the event time specified in this advisory', 'type': 'time_reference'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-092bcc3668a96bd4` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 60, "atm:controlledNASelement": {"label": "STL AIRPORT", "type": "nas:Airport"}, "atm:effectiveEndTime": "2026-05-18T18:18:30", "atm:e... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-14efb6f96dbcc899` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 60 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-1fac62c10fc36873` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'activated_diversion_recovery_tool_for'}` | {'label': 'STL Airport', 'type': 'airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. |
| `cand-29f1e5db9b12aea9` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T18:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-44808249ebdf2778` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 14:44 |
| `cand-53c083ea4eb2cd7e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'should_ensure_diversion_remarks_include'}` | {'label': 'DVRSN', 'type': 'flight_plan_remark_code'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-5524575c06129498` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZKC |
| `cand-626fcba3510612de` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T14:44:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-67371d27a1eed012` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T14:44:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:44 |
| `cand-713fe7ef1ca12b79` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-76c795ba3f863ea2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'are_not_automatically_exempt_when_ground_delay_program_or_ground_stop_exists...` | {'label': 'Ground Delay Program or Ground Stop at destination airport', 'type': 'traffic_management_program_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-833229eb2e50c49a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_constrained_facilities'}` | {'label': 'ZKC', 'type': 'facility_area'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZKC |
| `cand-b9dbdc5250267d53` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'will_still_receive'}` | {'label': 'EDCT', 'type': 'controlled_departure_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-c59bc2278e72ae21` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'will_close_for'}` | {'label': 'STL Airport', 'type': 'airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-cfae3018f8710e87` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_event_time'}` | {'label': '18/1445 - 18/1800', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1445 - 18/1800 |
| `cand-d18e893978302e42` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. |
| `cand-f8a4ad947e9fa1d6` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |

## ATCSCC-GOLD-094 / 2026-05-20:068

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=68
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 20

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH MESSAGE: FVAK21 PAWU 201504 WSI DDS:201506 VA ADVISORY DTG: 20260520/1504Z VAAC: ANCHORAGE VOLCANO: SHEVELUCH 300270 PSN: N5638 E16122 AREA: KAMCHATKA SOURCE ELEV: 10771 FT AMSL ADVISORY NR: 2026/112 INFO SOURCE: TOKYO VAAC. ERUPTION DETAILS: NOT PROVIDED OBS VA DTG: NOT PROVIDED OBS VA CLD: NOT PROVIDED FCST VA CLD +6HR: 20/2100Z NOT PROVIDED FCST VA CLD +12HR: 21/0300Z NOT PROVIDED FCST VA CLD +18HR: 21/0900Z NOT PROVIDED RMK: PLEASE SEE FVFE01 RJTD 201500 ISSUED BY TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. ...EVANS EFFECTIVE TIME: 200000-200000 SIGNATURE: 26/05/20 15:06 FAA.gov Home \| Privac...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02b47ef93754b27a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast volcanic ash cloud +12hr status` | not provided | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 21/0300Z NOT PROVIDED |
| `cand-155d9658218f338f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains remark` | Please see FVFE01 RJTD 201500 issued by Tokyo VAAC that describes conditions near the Anchorage VAAC area of responsibility. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PLEASE SEE FVFE01 RJTD 201500 ISSUED BY TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. |
| `cand-2efbcce4b5c23f42` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reported information source` | Tokyo VAAC | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: TOKYO VAAC. |
| `cand-30383679f9eeca03` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective time` | 200000-200000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-4622bce1cead85ea` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast volcanic ash cloud +6hr status` | not provided | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/2100Z NOT PROVIDED |
| `cand-50e87015046ad84b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-5335536ffa5c8aae` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed volcanic ash cloud status` | not provided | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: NOT PROVIDED |
| `cand-53c63f7159dba7ad` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-572766eaeff51308` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-5fa5f2be348daee3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names volcano` | Sheveluch | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-75b4c680749088e8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast volcanic ash cloud +18hr status` | not provided | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 21/0900Z NOT PROVIDED |
| `cand-9e6bd13f5925a339` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reported by advisory center` | Anchorage VAAC | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: ANCHORAGE |
| `cand-b5f6ae665ba2de3a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has location area` | Kamchatka | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA |
| `cand-ba1f45da429056ee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed volcanic ash date time status` | not provided | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: NOT PROVIDED |
| `cand-ba72f8e2a4350948` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T15:04:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 15:06 |
| `cand-c5ccf219f04d4bb2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `eruption details status` | not provided | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: NOT PROVIDED |
| `cand-d033d8c3864dfd52` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has source elevation` | 10771 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 10771 FT AMSL |
| `cand-f3fad562be61cf28` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 68 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-fa5cce3981271548` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has position` | N5638 E16122 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5638 E16122 |
| `cand-fcf7c38b70cdbfb7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory type` | Volcanic Activity Bulletin | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |

## ATCSCC-GOLD-095 / 2026-05-19:047

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=47
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 191453-191800 SIGNATURE: 26/05/19 14:53 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1220edfed626dd97` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 47 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-23fa55175460a571` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | FYI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-3f3f2febf2639c24` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was_signed_at` | 26/05/19 14:53 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:53 |
| `cand-40332ad0d858e598` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_status_change` | has been cancelled | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. |
| `cand-4b277cc73df27b76` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteReason` | OTHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-4b6f33c9a69725cc` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-19T14:53:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:53 |
| `cand-6a5404f803ab74c6` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 47 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-9554fff0ad9d742b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_message` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-9d751dd420bf273f` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-a39484ee27bd5128` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T14:53:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 14:53 |
| `cand-a3d03c44b63ecbff` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T14:53:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191453-191800 |
| `cand-b7d913fea7ab1b2b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-19T18:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |
| `cand-cc4a615de3c56403` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteType` | FCA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-cd1e5bfc1cb2e387` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T18:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191453-191800 |
| `cand-d95c150fd35b0dd5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 191453-191800 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |
| `cand-e8eb5d62fb065e39` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-f6fcbbc0ba3e43f1` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-19T14:53:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |

## ATCSCC-GOLD-096 / 2026-05-15:087

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=87
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 152323 WSI DDS:152324 VA ADVISORY DTG: 20260515/2323Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/567 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: POSS VA EMS EST VA DTG: 15/2300Z EST VA CLD: SFC/FL150 N1428 W09053 - N1427 W09052 - N1422 W09101 - N1426 W09102 - N1428 W09053 MOV SW 5KT FCST VA CLD +6HR: 16/0500Z SFC/FL150 N1431 W09103 - N1428 W09052 - N1427 W09052 - N1425 W09104 - N1431 W09103 FCST VA CLD +12HR: 16/1100Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09108 - N1426 W09110 - N1429 W09053 FCST VA CLD +18HR: 16/1700Z NO VA EXP R...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-082d129f24bc37ee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/1700Z |
| `cand-143eb272596d626d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N1428 W09052 |
| `cand-1a772bccf3884462` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: POSS VA EMS |
| `cand-241c0c8a67d6c1d9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/1100Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09108 - N1426 W09110 - N1429 W09053 |
| `cand-328a4691d01e7428` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 |
| `cand-36cbbdfd3b3eee77` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 87 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-3a4f53245e19c3d8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO |
| `cand-4aea799006c29164` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/1700Z NO VA EXP |
| `cand-502435770c3b27f0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-55ecfc9dc7a0c2d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: GUATEMALA |
| `cand-5724fe263a0ff0ca` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA FL/DIR BASED ON PREV VAA AND MDL GUIDANCE. |
| `cand-5cd72fec58edd750` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/0500Z |
| `cand-60b8be2a1892c726` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-6418973e2e434fc7` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-7454915df88c01ea` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a99f2d5b72ccca28` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T23:23:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 23:24 |
| `cand-a9dc95d049862406` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/0500Z SFC/FL150 N1431 W09103 - N1428 W09052 - N1427 W09052 - N1425 W09104 - N1431 W09103 |
| `cand-b2ca41d4eb52ee11` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 5KT |
| `cand-c50156e4798cb94c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS/CLDS NOT SEEN IN SAT AND WEBCAM DUE TO DENSE MET CLDS. |
| `cand-ca9024b8dfd626e3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDL FCST W-LY AND WSW-LY WINDS THRU T+12HRS. |
| `cand-cdb319281a370043` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/1100Z |
| `cand-d6c6be743cd51bba` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO", "value": 87}], "atm:initiativeComments": [{"e... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-eafc7c164c0a33e6` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO", "value": 87}], "atm:effectiveEndTime": [{"evi... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-f3bde2ac2f6be599` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 15/2300Z |

## ATCSCC-GOLD-097 / 2026-05-16:067

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=67
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 10

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION MESSAGE: DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 162225-170000 SIGNATURE: 26/05/16 22:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0033ec034c1130b9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_remarks` | associated restrictions | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-0eb4ebc52e98d56b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_status` | cancelled | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. |
| `cand-2f26a7fde84a912e` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T22:25:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162225-170000 |
| `cand-55b5671411505750` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION", "value": 67}], "atm:implementationStatus": [{"evidence_text... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-6f5ab98cdd9ecded` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162225-170000 |
| `cand-72b5ed7298b1f1e1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time_window` | 162225-170000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 162225-170000 |
| `cand-9cb5669445b095b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_message_topic` | reroute cancellation | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-c21a9636fbc6935c` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 67 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-d04f78766450362b` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T22:25:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 22:25 |
| `cand-f02184bdeff32c07` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_signature_timestamp` | 26/05/16 22:25 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 22:25 |

## ATCSCC-GOLD-098 / 2026-05-20:100

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=100
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202000 TO 210200 PROBABILITY OF EXTENSION: NONE REMARKS: ASSOCIATED RESTRICTIONS: 15 MIT VIA NOVON MODIFICATIONS: ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- KEWR KJFK KLGA KHPN KTEB >GREKI JUDDS CAM NOVON KENPA ZBW >NOVON KENPA TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KPDX KENPA CESNA EXHOS LWT PDT JKNOX < HHOOD6 KSEA KENPA CESNA EXHOS LWT MLP < GLASR3 TMI ID: RRDCC515 EFFECT...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-067b657da8a3429a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_route_modification` | KEWR/KJFK/KLGA/KHPN/KTEB >GREKI JUDDS CAM NOVON KENPA ZBW >NOVON KENPA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- KEWR KJFK KLGA KHPN KTEB >GREKI JUDDS CAM NOVON KENPA ZBW >NOVON KENPA |
| `cand-15eb4e40df94d9d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_name` | CAN_KENPA_WEST_2_PARTIAL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: CAN_KENPA_WEST_2_PARTIAL |
| `cand-1a063b65efd70d94` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_facilities_included` | CZY/ZBW/ZLC/ZMP/ZNY/ZSE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-1d1e6b1a0f970df4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_destination_route` | KPDX KENPA CESNA EXHOS LWT PDT JKNOX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KPDX KENPA CESNA EXHOS LWT PDT JKNOX |
| `cand-300da7a7e6d0e615` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time` | 202000-210200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202000-210200 |
| `cand-36715ca596c6ea85` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T18:07:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 18:07 |
| `cand-4624e617f72cf0fb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_traffic` | KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA |
| `cand-4da7f8dcb707c5e7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_tmi_id` | RRDCC515 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC515 |
| `cand-7537b51ff1040042` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 100 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-7b254fa64cbab110` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_associated_restriction` | 15 MIT VIA NOVON | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ASSOCIATED RESTRICTIONS: 15 MIT VIA NOVON |
| `cand-7f99f00583f77049` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_area` | ZOB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZOB |
| `cand-8a2502bfcb84bf85` | `S1_llm_only` | `freeform_or_unmapped_fact` | `valid_during` | ETD 202000 TO 210200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 202000 TO 210200 |
| `cand-8e612d8c8bf9d04f` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202000-210200 |
| `cand-a1a4cacb833f6def` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_destination_route` | GLASR3 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | < GLASR3 |
| `cand-aef57b9ab5176dde` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL", "value": 100}], "atm:controlledNASelement": [{"evidence_text": "AT... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-b0a39fc68a305d2d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-b25208c5c8c9f5b9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-bb9aa82fb77c5238` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202000-210200 |
| `cand-bc515aea4b759ba6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_destination_route` | KSEA KENPA CESNA EXHOS LWT MLP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KSEA KENPA CESNA EXHOS LWT MLP |
| `cand-cb47c8b2bb8393d5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | NONE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: NONE |
| `cand-ebab0ea8fc6f7f08` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CONSTRAINED AREA: ZOB", "label": "ZOB", "type": "nas:ARTCC"}, {"evidence_text": "INCLUDE TRAFFIC: KEWR/KHPN/... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-edb5fe644c95019e` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | NONE | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: NONE |
| `cand-f45a04bf55f14810` | `S1_llm_only` | `freeform_or_unmapped_fact` | `signature_timestamp` | 26/05/20 18:07 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 18:07 |

## ATCSCC-GOLD-099 / 2026-05-20:004

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=4
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 12

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 200016-200630 SIGNATURE: 26/05/20 00:16 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09dcf0957caefb45` | `S1_llm_only` | `freeform_or_unmapped_fact` | `caused_by` | thunderstorms | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-144ffa453360aa95` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces_event_time_window` | 20/0030 - 20/0600 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-26ad29a873d68c3f` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T00:16:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:16 |
| `cand-2cce8c5d8ca4c4c7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_updates_will_follow_if_necessary` | updates will follow if necessary | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-2f1bb9bba9bc97f3` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T06:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200016-200630 |
| `cand-399f74b82304536c` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:16:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200016-200630 |
| `cand-3aa7373c8655ea20` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 4, "atm:controlledNASelement": {"name": "MEM Airport", "type": "nas:Airport"}, "atm:effectiveEndTime": "2026-05-20T06:30:00", "atm:eff... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-3fd008fcfd7c2e0a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-42763d155b857421` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect_airborne_holding_into` | MEM AIRPORT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-4b6d692f2a1024f8` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 4 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-bc5e093c7a81740c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect_arrival_delays_into` | MEM AIRPORT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-db8f2efba55faf81` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is` | 200016-200630 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200016-200630 |

## ATCSCC-GOLD-100 / 2026-05-17:071

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=71
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 172057 WSI DDS:172058 VA ADVISORY DTG: 20260517/2057Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0005 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/488 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: OCNL VA EMS EST VA DTG: 17/2030Z EST VA CLD: SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747 MOV NW 5KT FCST VA CLD +6HR: 18/0230Z SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748 FCST VA CLD +12HR: 18/0830Z NO VA EXP FCST VA CLD +18HR: 18/1430Z NO VA EXP RMK: VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. VA EMS MAY CON...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1e0a6fecccf5c919` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_volcano_position'}` | {'class': 'position', 'text': 'S0005 W07739'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: REVENTADOR 352010 PSN: S0005 W07739 |
| `cand-1e808a9782ce9cd3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_expectation'}` | {'class': 'forecast_status', 'text': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 18/0830Z NO VA EXP |
| `cand-221e3f87fa3644c1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'movement_direction_speed'}` | {'class': 'movement', 'text': 'NW 5KT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 5KT |
| `cand-3b0a36b1ad38fa22` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'expected_movement'}` | {'class': 'movement_expectation', 'text': 'WNW MVMT EXP THRU T+6'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. WNW MVMT EXP THRU T+6. |
| `cand-3b26872dbf10d0e8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'source_elevation_is'}` | {'class': 'elevation', 'text': '11686 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-3c129496de69eca7` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR", "value": 71}], "atm:effectiveEndTime": [... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-413fa55ee0d1def5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'based_on'}` | {'class': 'forecast_basis', 'text': 'MDL GUIDANCE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST BASED ON MDL GUIDANCE. |
| `cand-53f20d6b6f02e086` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is_bulletin_title'}` | {'class': 'bulletin_title', 'text': 'VOLCANIC ACTIVITY BULLETIN - REVENTADOR'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-571357d0a57cbc2a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'eruption_details_state'}` | {'class': 'eruption_activity', 'text': 'OCNL VA EMS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: OCNL VA EMS |
| `cand-666948e73d297aa6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'not_visible_reason'}` | {'class': 'weather_condition', 'text': 'MET CLD CVR'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. |
| `cand-6aef79a8fac754fa` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/1430Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 18/1430Z NO VA EXP |
| `cand-763b6a40d9567478` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_advisory_datetime'}` | {'class': 'datetime_utc', 'text': '20260517/2057Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260517/2057Z |
| `cand-7d58a7f9dac92d6f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/0230Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 18/0230Z |
| `cand-86b6bf8993bc4a42` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-9577fd6c6996030c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'may_continue'}` | {'class': 'activity_continuation', 'text': 'CONT.'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
| `cand-95875ff45a80e25c` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T20:57:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:58 |
| `cand-96ccc82d12d3d972` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_extent'}` | {'class': 'airspace_extent', 'text': 'SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 18/0230Z SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748 |
| `cand-b2518bbe15e92a70` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'located_in_area'}` | {'class': 'area', 'text': 'ECUADOR'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-c27d04ed92be503c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated_ash_datetime'}` | {'class': 'datetime_utc', 'text': '17/2030Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 17/2030Z |
| `cand-cc6cd296553847ab` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/0830Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 18/0830Z NO VA EXP |
| `cand-e55084e25d50561e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_advisory_number'}` | {'class': 'advisory_number', 'text': '2026/488'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/488 |
| `cand-e7551171ba5506b2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_expectation'}` | {'class': 'forecast_status', 'text': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 18/1430Z NO VA EXP |
| `cand-edc6c0a672b53c5e` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 71 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-f6087b25a63f36fc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated_ash_extent'}` | {'class': 'airspace_extent', 'text': 'SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747 |
| `cand-fb4c6cd04f04f2d4` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
