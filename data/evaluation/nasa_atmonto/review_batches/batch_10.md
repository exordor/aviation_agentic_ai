# NASA ATMONTO Gold Review batch_10

- Samples: `ATCSCC-GOLD-091` to `ATCSCC-GOLD-100`
- Records: 10
- Candidate clusters: 284

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-091 / 2026-05-19:068

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=68
- Candidate class: `GroundStopTMI`
- Current status: `reviewed`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAH ELEMENT TYPE: APT ADL TIME: 1742Z GROUND STOP PERIOD: 19/1732Z - 19/1845Z DEP FACILITIES INCLUDED: (Manual) ZTL ZHU PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 401 / 66 / 50 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: RWY-TAXI / DISABLED AIRCRAFT COMMENTS: DISABLED AC ON RWY 8R, USERS CAN EXPECT HOLDING DURING THIS TIME EFFECTIVE TIME: 191746-191945 SIGNATURE: 26/05/19 17:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00863fa40c323c56` | `S1_llm_only` | `canonical_fact` | `'can_expect'}` | {'label': 'holding during this time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT HOLDING DURING THIS TIME |
| `cand-07672b9cb81ff9a1` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T18:45:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 19/1732Z - 19/1845Z |
| `cand-0e8fa43a5f5a3f6f` | `S1_llm_only` | `canonical_fact` | `'has_previous_delays'}` | {'label': '0 / 0 / 0'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-1627cff4285a2b80` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAH | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAH |
| `cand-24769a3f4d16458b` | `S1_llm_only` | `canonical_fact` | `'identifies_controlled_airport'}` | {'label': 'IAH'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-25f36248f3080d5a` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | DISABLED AC ON RWY 8R, USERS CAN EXPECT HOLDING DURING THIS TIME | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | COMMENTS: DISABLED AC ON RWY 8R, USERS CAN EXPECT HOLDING DURING THIS TIME |
| `cand-501fdef0f4b5eb7e` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZHU |
| `cand-5b4c4c1a2fb40e49` | `S1_llm_only` | `canonical_fact` | `'has_effective_time'}` | {'label': '191746-191945'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191746-191945 |
| `cand-5e6221ec8bed1dcd` | `S1_llm_only` | `canonical_fact` | `'states_ctl_element'}` | {'label': 'IAH'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAH |
| `cand-61c984e0c7e6fdb0` | `S1_llm_only` | `canonical_fact` | `'announces_ground_stop'}` | {'label': 'ground stop'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-6fe8b259962d0d47` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 4}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-79bec4129ac48582` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-19T17:42:00Z | `{"repaired_accepted": 1}` | `{}` | ADL TIME: 1742Z |
| `cand-7cf70501fbd4f028` | `S1_llm_only` | `canonical_fact` | `'has_period'}` | {'label': '19/1732Z - 19/1845Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 19/1732Z - 19/1845Z |
| `cand-824ed204a602b69f` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 68 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-923c53902c739a03` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T17:32:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 19/1732Z - 19/1845Z |
| `cand-9277f2ce083acc9c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T19:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191746-191945 |
| `cand-94e82e7b095bbde3` | `S1_llm_only` | `canonical_fact` | `'gives_advisory_time'}` | {'label': '1742Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1742Z |
| `cand-95c0aa5be5f117ec` | `S1_llm_only` | `canonical_fact` | `'has_new_delays'}` | {'label': '401 / 66 / 50'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 401 / 66 / 50 |
| `cand-96149ed9af33b92e` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZTL ZHU'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZHU |
| `cand-9e411d2aaf0a6cef` | `S1_llm_only` | `canonical_fact` | `'states_element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-a12ea7fcaeff4a15` | `S1_llm_only` | `canonical_fact` | `'names_control_facility'}` | {'label': 'ZHU'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-a362e21cba43ea6d` | `S1_llm_only` | `canonical_fact` | `'located_on'}` | {'label': 'RWY 8R'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISABLED AC ON RWY 8R |
| `cand-a4d960dd35eb405e` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | IAH | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAH ELEMENT TYPE: APT ADL TIME: 1742Z GROUND STOP PERIOD: 19/1732Z - 19/1845Z |
| `cand-aa425f4d27a70349` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T17:47:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/19 17:47 |
| `cand-b3e7891c40ba222a` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | rwy-taxi / disabled aircraft | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: RWY-TAXI / DISABLED AIRCRAFT |
| `cand-c7f55782dc4397e0` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-ca065d3851981a0d` | `S1_llm_only` | `canonical_fact` | `'has_probability_of_extension'}` | {'label': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d3267125fbb1c679` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:nas:Airport/IAH | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAH |
| `cand-d91bd3ecf89feeaf` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | runway | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: RWY-TAXI / DISABLED AIRCRAFT |
| `cand-f0de01a539ebdf6e` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZHU |
| `cand-f53d732bd1978f03` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T17:46:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191746-191945 |
| `cand-f90f6d6135cc0880` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAH | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `cand-feec77fde8aaf13d` | `S1_llm_only` | `canonical_fact` | `'has_impacting_condition'}` | {'label': 'RWY-TAXI / DISABLED AIRCRAFT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: RWY-TAXI / DISABLED AIRCRAFT |

## ATCSCC-GOLD-092 / 2026-05-15:075

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=75
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 45

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z CUMULATIVE PROGRAM PERIOD: 15/1700Z - 16/0359Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1042 / 180 / 55 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1875 / 273 / 99 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LOW CEILINGS COMMENTS: EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP EFFECTIVE TIME: 152115-152315 SIGNATURE: 26/05/15 21:16 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Vi...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01caef5b9fd17050` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | weather | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-02ab35bbdaf5cc3a` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYQB | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-02f8f0f8fa0252d7` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-06cc77b29a88cedd` | `S1_llm_only` | `canonical_fact` | `'has cumulative program period'}` | {'label': '15/1700Z - 16/0359Z', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 15/1700Z - 16/0359Z |
| `cand-099564312b805a82` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | weather | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-0bd0de4b200ac98b` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | BOS | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BOS ELEMENT TYPE: APT |
| `cand-131458e8e346fca9` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-1591d5ad63009bb2` | `S1_llm_only` | `canonical_fact` | `'describes action as'}` | {'label': 'GROUND STOP', 'type': 'traffic_management_action'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP |
| `cand-1776aa4bf22a2172` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-2ee18a4b4beb8eb1` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather / low ceilings impacting_condition | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-33e0b1279de53567` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP |
| `cand-348e03a273a38374` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYTZ | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-37b7e50d0743db78` | `S1_llm_only` | `canonical_fact` | `'has ground stop period'}` | {'label': '15/2059Z - 15/2215Z', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 15/2059Z - 15/2215Z |
| `cand-3f1450c28b3cdc46` | `S1_llm_only` | `canonical_fact` | `'reports previous total maximum average delays'}` | {'label': '1042 / 180 / 55', 'type': 'delay_metrics'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1042 / 180 / 55 |
| `cand-468596cb9f9aa7d0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP |
| `cand-50c9bdcac867731f` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-5a0d881dc10d6622` | `S1_llm_only` | `canonical_fact` | `'names control element'}` | {'label': 'BOS', 'type': 'control_element'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BOS |
| `cand-5fcffd728b2b740f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingConditionMessage` | WEATHER / LOW CEILINGS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-61a4d428a0e19e70` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T21:15:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152115-152315 |
| `cand-62f4cdbd25300bc8` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYOW | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-64811c22b796f7d3` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-65ee3ac2a5395466` | `S1_llm_only` | `canonical_fact` | `'includes departure facilities'}` | {'label': 'ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB', 'type': 'facility_list'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-68064cb111411651` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-6eac13eda3ecf390` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYUL | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-72db67b9db2ce001` | `S1_llm_only` | `canonical_fact` | `'gives probability of extension'}` | {'label': 'MEDIUM', 'type': 'extension_probability'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-772764549167a379` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-15T21:16:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 21:16 |
| `cand-7e6a8f7a689821d9` | `S1_llm_only` | `canonical_fact` | `'has effective time'}` | {'label': '152115-152315', 'type': 'effective_time_interval'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 152115-152315 |
| `cand-807b97f95d919f05` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYHZ | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-85268ea14582b454` | `S1_llm_only` | `canonical_fact` | `'has advisory identifier'}` | {'label': 'ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP', 'type': 'advisory_identifier'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP |
| `cand-8838ae231d88e9d9` | `S1_llm_only` | `canonical_fact` | `'names impacting condition'}` | {'label': 'WEATHER / LOW CEILINGS', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / LOW CEILINGS |
| `cand-8938cb4b532d46b9` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYYZ | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-8fe84b52580edf10` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-15T21:14:00Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ADT TIME: 2114Z |
| `cand-90c9ddeeeb081f3e` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-15T21:16:00Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-9cd960e90dc3c62d` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | BOS | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-a562e37783b7efe9` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZBW CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-a6e11bdab13ad19d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T23:15:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152115-152315 |
| `cand-aab5d1cb5ea500f9` | `S1_llm_only` | `canonical_fact` | `'states expected follow-on action'}` | {'label': 'GDP TO BE REVISED FOLLOWING THE GROUND STOP', 'type': 'follow_on_action'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: EXPECT GDP TO BE REVISED FOLLOWING THE GROUND STOP |
| `cand-aae92cdafb1f431f` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-be011a44b1aecbb9` | `S1_llm_only` | `canonical_fact` | `'reports new total maximum average delays'}` | {'label': '1875 / 273 / 99', 'type': 'delay_metrics'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1875 / 273 / 99 |
| `cand-c3351b524ccbda81` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 75 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-ccbfb35f30512e8a` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 75 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP |
| `cand-e975e927ac3c95d1` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BOS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: BOS |
| `cand-f3fdcd0fbba029d1` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T21:15:00Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-fa7cc25679b63c13` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T23:15:00Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP ... CTL ELEMENT: BOS ELEMENT TYPE: APT ADL TIME: 2114Z GROUND STOP PERIOD: 15/2059Z - 15/2215Z ... PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / LO... |
| `cand-fea52f54697764de` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-093 / 2026-05-18:060

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=60
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 18/1445 - 18/1800 CONSTRAINED FACILITIES: ZKC THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. EFFECTIVE TIME: 181444-181830 SIGNATURE: 26/05/18 14:44 FAA.gov Home \| Privacy Policy \| Web Policies &...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04e26b944dffdd8a` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | CONSTRAINED FACILITIES: ZKC | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZKC |
| `cand-09bb6a84bdcb8045` | `S1_llm_only` | `canonical_fact` | `'will_close_at_end_of'}` | {'label': 'the event time specified in this advisory', 'type': 'time_reference'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-0e819541e6805145` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DELAY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-14efb6f96dbcc899` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 60 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-26a1a6bb2008d57b` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. | `{"repaired_accepted": 1}` | `{}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. |
| `cand-29f1e5db9b12aea9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T18:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-2a08086ed539a6cd` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCR... | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-2ec2441fd533cf45` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T18:14:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-561356876a787410` | `S1_llm_only` | `canonical_fact` | `'will_close_for'}` | {'label': 'STL Airport', 'type': 'airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-56392a5bcdbd4492` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T18:30:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-57560f139586511a` | `S1_llm_only` | `canonical_fact` | `'are_not_automatically_exempt_when_ground_delay_program_or_ground_stop_exists...` | {'label': 'Ground Delay Program or Ground Stop at destination airport', 'type': 'traffic_management_program_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-626fcba3510612de` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T14:44:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-67371d27a1eed012` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T14:44:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:44 |
| `cand-6a8751830cc894c8` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T14:44:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:44 |
| `cand-6bf115c388c9c967` | `S1_llm_only` | `canonical_fact` | `'identifies_constrained_facilities'}` | {'label': 'ZKC', 'type': 'facility_area'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZKC |
| `cand-713fe7ef1ca12b79` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-76ca50f592d94547` | `S1_llm_only` | `canonical_fact` | `'should_ensure_diversion_remarks_include'}` | {'label': 'DVRSN', 'type': 'flight_plan_remark_code'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-7b675e048434f53e` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-18T14:44:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-9a9e0435d761ce78` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. | `{"repaired_accepted": 1}` | `{}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-b2f246ec34137756` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T18:18:30 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-bf8c6a3a1fb37fcb` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | STL AIRPORT | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-c427512e6e92d4ef` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STOP | `{"repaired_accepted": 1}` | `{}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-d10ca7a50b34a2d3` | `S1_llm_only` | `canonical_fact` | `'will_still_receive'}` | {'label': 'EDCT', 'type': 'controlled_departure_time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-e1bfc10d864d1ec4` | `S1_llm_only` | `canonical_fact` | `'states_event_time'}` | {'label': '18/1445 - 18/1800', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1445 - 18/1800 |
| `cand-e39d5b87da5dcf3e` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T14:44:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-e8ddef3480df7175` | `S1_llm_only` | `canonical_fact` | `'activated_diversion_recovery_tool_for'}` | {'label': 'STL Airport', 'type': 'airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. |
| `cand-fe791620f05d7cf2` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZKC |

## ATCSCC-GOLD-094 / 2026-05-20:068

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=68
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
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
| `cand-15318c9b9a504aca` | `S1_llm_only` | `canonical_fact` | `reported information source` | Tokyo VAAC | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: TOKYO VAAC. |
| `cand-190b19793af9468b` | `S1_llm_only` | `canonical_fact` | `has position` | N5638 E16122 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5638 E16122 |
| `cand-20e105646d021bc7` | `S1_llm_only` | `canonical_fact` | `contains remark` | Please see FVFE01 RJTD 201500 issued by Tokyo VAAC that describes conditions near the Anchorage VAAC area of responsibility. | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PLEASE SEE FVFE01 RJTD 201500 ISSUED BY TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. |
| `cand-53c63f7159dba7ad` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-572766eaeff51308` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-59338804e2e00222` | `S1_llm_only` | `canonical_fact` | `eruption details status` | not provided | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: NOT PROVIDED |
| `cand-6a9b01b2d1d3856a` | `S1_llm_only` | `canonical_fact` | `observed volcanic ash date time status` | not provided | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: NOT PROVIDED |
| `cand-7e128763c442d189` | `S1_llm_only` | `canonical_fact` | `has location area` | Kamchatka | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA |
| `cand-82fc59eb02b85ef6` | `S1_llm_only` | `canonical_fact` | `forecast volcanic ash cloud +12hr status` | not provided | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 21/0300Z NOT PROVIDED |
| `cand-a6b207d6e648444f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1}` |  |
| `cand-a7dd2c39be36ab18` | `S1_llm_only` | `canonical_fact` | `forecast volcanic ash cloud +18hr status` | not provided | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 21/0900Z NOT PROVIDED |
| `cand-ace88d91890ab3ed` | `S1_llm_only` | `canonical_fact` | `reported by advisory center` | Anchorage VAAC | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: ANCHORAGE |
| `cand-b6afdd48dd5cd94f` | `S1_llm_only` | `canonical_fact` | `forecast volcanic ash cloud +6hr status` | not provided | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/2100Z NOT PROVIDED |
| `cand-ba72f8e2a4350948` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T15:04:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 15:06 |
| `cand-c7048fafc0c77182` | `S1_llm_only` | `canonical_fact` | `effective time` | 200000-200000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-c73311ac85f29286` | `S1_llm_only` | `canonical_fact` | `names volcano` | Sheveluch | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-d165865962748178` | `S1_llm_only` | `canonical_fact` | `has source elevation` | 10771 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 10771 FT AMSL |
| `cand-e824d7ef6ef0b1b3` | `S1_llm_only` | `canonical_fact` | `has advisory type` | Volcanic Activity Bulletin | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-f3fad562be61cf28` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 68 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-fe0da22d36423d99` | `S1_llm_only` | `canonical_fact` | `observed volcanic ash cloud status` | not provided | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: NOT PROVIDED |

## ATCSCC-GOLD-095 / 2026-05-19:047

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=47
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
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
| `cand-0d0f0b3919bc13a8` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | FCA | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-103dc703946f5146` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-1220edfed626dd97` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 47 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-4497725adf6f0555` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T14:53:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:53 |
| `cand-48b769eb5f3bd730` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T18:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |
| `cand-4ad329a720562a5d` | `S1_llm_only` | `canonical_fact` | `has_status_change` | has been cancelled | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. |
| `cand-4c67bc0c63e9be17` | `S1_llm_only` | `canonical_fact` | `has_message` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-57e73df87759e13f` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 47 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-6795d233730878ea` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-8484a779672cae41` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-874823263ac57ffe` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T14:53:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |
| `cand-a39484ee27bd5128` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T14:53:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 14:53 |
| `cand-a3d03c44b63ecbff` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T14:53:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191453-191800 |
| `cand-acea76b0bfb13fc1` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | OTHER | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-cd1e5bfc1cb2e387` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T18:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191453-191800 |
| `cand-e8f53247193e3d01` | `S1_llm_only` | `canonical_fact` | `was_signed_at` | 26/05/19 14:53 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:53 |
| `cand-f48e96cfb6d98726` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 191453-191800 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |

## ATCSCC-GOLD-096 / 2026-05-15:087

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=87
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 25

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
| `cand-36cbbdfd3b3eee77` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 87 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 4}` | `{}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-3a4f53245e19c3d8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO |
| `cand-4aea799006c29164` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/1700Z NO VA EXP |
| `cand-502435770c3b27f0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-55ecfc9dc7a0c2d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: GUATEMALA |
| `cand-5724fe263a0ff0ca` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA FL/DIR BASED ON PREV VAA AND MDL GUIDANCE. |
| `cand-5cd72fec58edd750` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/0500Z |
| `cand-60b8be2a1892c726` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-6418973e2e434fc7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-67078c46e9f87fef` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-15T23:24:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/15 23:24 |
| `cand-7454915df88c01ea` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a37f568b70aa99d5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T15:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a99f2d5b72ccca28` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-15T23:23:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 23:24 |
| `cand-a9dc95d049862406` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/0500Z SFC/FL150 N1431 W09103 - N1428 W09052 - N1427 W09052 - N1425 W09104 - N1431 W09103 |
| `cand-b2ca41d4eb52ee11` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 5KT |
| `cand-c50156e4798cb94c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS/CLDS NOT SEEN IN SAT AND WEBCAM DUE TO DENSE MET CLDS. |
| `cand-c6baef3137e877a2` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-ca9024b8dfd626e3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDL FCST W-LY AND WSW-LY WINDS THRU T+12HRS. |
| `cand-cdb319281a370043` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/1100Z |
| `cand-f3bde2ac2f6be599` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 15/2300Z |

## ATCSCC-GOLD-097 / 2026-05-16:067

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=67
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 13

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION MESSAGE: DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 162225-170000 SIGNATURE: 26/05/16 22:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-024443dcc4dad155` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"repaired_accepted": 1}` | `{}` | DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-0e2fad3244bb7ffa` | `S1_llm_only` | `canonical_fact` | `has_effective_time_window` | 162225-170000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 162225-170000 |
| `cand-15672c022942c78e` | `S1_llm_only` | `canonical_fact` | `has_remarks` | associated restrictions | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-2f26a7fde84a912e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T22:25:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162225-170000 |
| `cand-57fc15b97eda7373` | `S1_llm_only` | `canonical_fact` | `has_signature_timestamp` | 26/05/16 22:25 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 22:25 |
| `cand-6f5ab98cdd9ecded` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162225-170000 |
| `cand-723f732c408429a6` | `S1_llm_only` | `canonical_fact` | `has_status` | cancelled | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. |
| `cand-a12fd7682e4ac5ee` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-a9a81a2f09362a97` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T22:25:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 22:25 |
| `cand-c1d2d5458b9f225c` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-c21a9636fbc6935c` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 67 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-d04f78766450362b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-16T22:25:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 22:25 |
| `cand-d5aec2541328395e` | `S1_llm_only` | `canonical_fact` | `has_message_topic` | reroute cancellation | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |

## ATCSCC-GOLD-098 / 2026-05-20:100

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=100
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 55

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202000 TO 210200 PROBABILITY OF EXTENSION: NONE REMARKS: ASSOCIATED RESTRICTIONS: 15 MIT VIA NOVON MODIFICATIONS: ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- KEWR KJFK KLGA KHPN KTEB >GREKI JUDDS CAM NOVON KENPA ZBW >NOVON KENPA TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KPDX KENPA CESNA EXHOS LWT PDT JKNOX < HHOOD6 KSEA KENPA CESNA EXHOS LWT MLP < GLASR3 TMI ID: RRDCC515 EFFECT...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01fd977b719ae683` | `S1_llm_only` | `canonical_fact` | `effective_time` | 202000-210200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202000-210200 |
| `cand-026168e4a96fe8a3` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteReason` | WEATHER | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-02c50f5a9e223346` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:20:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202000-210200 |
| `cand-0525f733107968d9` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZOB | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED AREA: ZOB |
| `cand-0a4ffa19360339c4` | `S1_llm_only` | `canonical_fact` | `includes_traffic` | KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA |
| `cand-147ce357b2d1ea7d` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:20:00 | `{"repaired_accepted": 1}` | `{}` | VALID: ETD 202000 TO 210200 |
| `cand-16d7cc3be166f6f4` | `S1_llm_only` | `canonical_fact` | `has_destination_route` | KSEA KENPA CESNA EXHOS LWT MLP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KSEA KENPA CESNA EXHOS LWT MLP |
| `cand-1bd4133de899617b` | `S1_llm_only` | `canonical_fact` | `has_destination_route` | GLASR3 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | < GLASR3 |
| `cand-2d2ab6144802e2f4` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-31c11b428c9492f3` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-36715ca596c6ea85` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T18:07:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 18:07 |
| `cand-386c642b4ce78eed` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | NONE | `{"repaired_accepted": 1}` | `{}` | NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE FLIGHT STATUS: ALL_FLIGHTS VALID:... |
| `cand-3b55aa2c878c7630` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZSE | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-3bed8da59c07e574` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | CZY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-436967e22c7bec98` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZMP | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-49b029222fb5249a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZBW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA |
| `cand-4b13a0d9d7c01bd6` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-4fff2ba7f15e676c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:02:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202000-210200 |
| `cand-537cb8540c26e894` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ASSOCIATED RESTRICTIONS: 15 MIT VIA NOVON MODIFICATIONS: ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- KEWR KJFK KLGA KHPN KTEB >GR... | `{"repaired_accepted": 1}` | `{}` | NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE FLIGHT STATUS: ALL_FLIGHTS VALID:... |
| `cand-5599116cce9c0f4f` | `S1_llm_only` | `canonical_fact` | `has_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-563657b3f142dda7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | NONE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-59dfed9768bda4aa` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CZY | `{"repaired_accepted": 1}` | `{}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-6126e1c5d9f355df` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-20T18:07:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-62aaded113c0cff0` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-64f950686fa732d2` | `S1_llm_only` | `canonical_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-7537b51ff1040042` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 100 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-772253684c2a66c2` | `S1_llm_only` | `canonical_fact` | `valid_during` | ETD 202000 TO 210200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 202000 TO 210200 |
| `cand-7c9c7bd2b4930499` | `S1_llm_only` | `canonical_fact` | `has_constrained_area` | ZOB | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZOB |
| `cand-7f89732a02d0aff0` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T18:07:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 18:07 |
| `cand-806b7b523d3146ab` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteType` | ROUTE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-85aa3dc24d3ea2ab` | `S1_llm_only` | `canonical_fact` | `has_route_modification` | KEWR/KJFK/KLGA/KHPN/KTEB >GREKI JUDDS CAM NOVON KENPA ZBW >NOVON KENPA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- KEWR KJFK KLGA KHPN KTEB >GREKI JUDDS CAM NOVON KENPA ZBW >NOVON KENPA |
| `cand-8e612d8c8bf9d04f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202000-210200 |
| `cand-94f9b959bdfca1b7` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZBW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-96262b327f7385aa` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE FLIGHT STATUS: ALL_FLIGHTS VALID:... |
| `cand-9ac51ec2121fba58` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-a6c878b8b7ab1682` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | ASSOCIATED RESTRICTIONS: 15 MIT VIA NOVON | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-b050366e654cbc17` | `S1_llm_only` | `canonical_fact` | `has_tmi_id` | RRDCC515 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC515 |
| `cand-b6f2a9f5e2b75187` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:02:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-b7abb351af6faae3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:20:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-bb9aa82fb77c5238` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202000-210200 |
| `cand-bbff66c0d47236ed` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | NONE | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: NONE |
| `cand-c32840528f7b3206` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLC | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-c8d22bbfebe2c11d` | `S1_llm_only` | `canonical_fact` | `has_destination_route` | KPDX KENPA CESNA EXHOS LWT PDT JKNOX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KPDX KENPA CESNA EXHOS LWT PDT JKNOX |
| `cand-cb0d0fed876ee3f1` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: CAN_KENPA_WEST_2_PARTIAL CONSTRAINED AREA: ZOB REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB/ZBW DEPARTURES TO KPDX/KSEA FACILITIES INCLUDED: CZ... |
| `cand-ce3cb200710f0c74` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:02:00 | `{"repaired_accepted": 1}` | `{}` | VALID: ETD 202000 TO 210200 |
| `cand-cfa1caa1e24cc208` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-de394b103034fad2` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZLC | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-e50f6cc92dd74b52` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-e800306882a6765a` | `S1_llm_only` | `canonical_fact` | `signature_timestamp` | 26/05/20 18:07 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 18:07 |
| `cand-edb5fe644c95019e` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | NONE | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: NONE |
| `cand-f203e6ae880a3087` | `S1_llm_only` | `canonical_fact` | `has_advisory_name` | CAN_KENPA_WEST_2_PARTIAL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: CAN_KENPA_WEST_2_PARTIAL |
| `cand-f3a7ff3ce352127c` | `S1_llm_only` | `canonical_fact` | `has_associated_restriction` | 15 MIT VIA NOVON | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ASSOCIATED RESTRICTIONS: 15 MIT VIA NOVON |
| `cand-fe5705295f2d6b5a` | `S1_llm_only` | `canonical_fact` | `has_facilities_included` | CZY/ZBW/ZLC/ZMP/ZNY/ZSE | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |
| `cand-fe7a36bea932bed5` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {"@id": "nas:ARTCC/ZOB"} | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-ffaddbb40e63e399` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZSE | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZLC/ZMP/ZNY/ZSE |

## ATCSCC-GOLD-099 / 2026-05-20:004

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=4
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 200016-200630 SIGNATURE: 26/05/20 00:16 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-26ad29a873d68c3f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T00:16:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:16 |
| `cand-2ca5cf75b611e7d6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 4 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-2f1bb9bba9bc97f3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T06:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200016-200630 |
| `cand-399f74b82304536c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:16:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200016-200630 |
| `cand-4abe9b6a1915a3be` | `S1_llm_only` | `canonical_fact` | `is` | 200016-200630 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200016-200630 |
| `cand-4b6d692f2a1024f8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 4 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-4c2381e2c4e6a40f` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingConditionMessage` | EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL... | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-4ca1145be59b411b` | `S1_llm_only` | `canonical_fact` | `maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-61b1b1310ba08eba` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | weather | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-64bed96bbd457385` | `S1_llm_only` | `canonical_fact` | `caused_by` | thunderstorms | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-81b54c1b61b7478a` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | MEM Airport | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-91170ebd290cc966` | `S1_llm_only` | `canonical_fact` | `states_updates_will_follow_if_necessary` | updates will follow if necessary | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-93db1731e1e24c98` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:16:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-b0465426ea06276c` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T06:30:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-bb94bc4fb26d6fb5` | `S1_llm_only` | `canonical_fact` | `can_expect_arrival_delays_into` | MEM AIRPORT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-f607542441e32871` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | thunderstorms | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-f8e246eb5f85fda7` | `S1_llm_only` | `canonical_fact` | `can_expect_airborne_holding_into` | MEM AIRPORT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-fa9399d3400c14b6` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL... | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-fd63bd5f29f6e12d` | `S1_llm_only` | `canonical_fact` | `announces_event_time_window` | 20/0030 - 20/0600 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |

## ATCSCC-GOLD-100 / 2026-05-17:071

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=71
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 30

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 172057 WSI DDS:172058 VA ADVISORY DTG: 20260517/2057Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0005 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/488 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: OCNL VA EMS EST VA DTG: 17/2030Z EST VA CLD: SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747 MOV NW 5KT FCST VA CLD +6HR: 18/0230Z SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748 FCST VA CLD +12HR: 18/0830Z NO VA EXP FCST VA CLD +18HR: 18/1430Z NO VA EXP RMK: VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. VA EMS MAY CON...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0043172ece849d92` | `S1_llm_only` | `canonical_fact` | `'expected_movement'}` | {'class': 'movement_expectation', 'text': 'WNW MVMT EXP THRU T+6'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. WNW MVMT EXP THRU T+6. |
| `cand-04e080f334f86f9b` | `S1_llm_only` | `canonical_fact` | `'forecast_expectation'}` | {'class': 'forecast_status', 'text': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 18/1430Z NO VA EXP |
| `cand-0788bdad7b921deb` | `S1_llm_only` | `canonical_fact` | `'located_in_area'}` | {'class': 'area', 'text': 'ECUADOR'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-1f90573ef4dae869` | `S1_llm_only` | `canonical_fact` | `'estimated_ash_datetime'}` | {'class': 'datetime_utc', 'text': '17/2030Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 17/2030Z |
| `cand-2e5d6fe7ff72c3d1` | `S1_llm_only` | `canonical_fact` | `'not_visible_reason'}` | {'class': 'weather_condition', 'text': 'MET CLD CVR'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. |
| `cand-30c9bfdeb69a409c` | `S1_llm_only` | `canonical_fact` | `'based_on'}` | {'class': 'forecast_basis', 'text': 'MDL GUIDANCE'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST BASED ON MDL GUIDANCE. |
| `cand-3b30320e058a48d2` | `S1_llm_only` | `canonical_fact` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/0230Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 18/0230Z |
| `cand-3cd8a846fd12c7aa` | `S1_llm_only` | `canonical_fact` | `'eruption_details_state'}` | {'class': 'eruption_activity', 'text': 'OCNL VA EMS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: OCNL VA EMS |
| `cand-50e92732f3853355` | `S1_llm_only` | `canonical_fact` | `'has_advisory_number'}` | {'class': 'advisory_number', 'text': '2026/488'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/488 |
| `cand-58824fb5a501dfc3` | `S1_llm_only` | `canonical_fact` | `'movement_direction_speed'}` | {'class': 'movement', 'text': 'NW 5KT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 5KT |
| `cand-5b869eb294288418` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | met cld cvr | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. |
| `cand-66ab6ac13ac97ee5` | `S1_llm_only` | `canonical_fact` | `'forecast_extent'}` | {'class': 'airspace_extent', 'text': 'SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 18/0230Z SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748 |
| `cand-6dcf912bdeab0e74` | `S1_llm_only` | `canonical_fact` | `'estimated_ash_extent'}` | {'class': 'airspace_extent', 'text': 'SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747 |
| `cand-71dc1622d738d609` | `S1_llm_only` | `canonical_fact` | `'is_bulletin_title'}` | {'class': 'bulletin_title', 'text': 'VOLCANIC ACTIVITY BULLETIN - REVENTADOR'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-82b1a94b2721ae83` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - REVENTADOR | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-82d396049150757b` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T17:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-86b6bf8993bc4a42` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-8e211f350e2c1a6f` | `S1_llm_only` | `canonical_fact` | `'has_volcano_position'}` | {'class': 'position', 'text': 'S0005 W07739'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: REVENTADOR 352010 PSN: S0005 W07739 |
| `cand-95875ff45a80e25c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-17T20:57:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:58 |
| `cand-aa18ccacf46e5cb8` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T17:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-afe7396785d7f8a5` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-17T20:58:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:58 |
| `cand-b7bc53fa0c4b32e0` | `S1_llm_only` | `canonical_fact` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/0830Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 18/0830Z NO VA EXP |
| `cand-b99df757e16e0bda` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 71 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/488 |
| `cand-b9b3b70214007e05` | `S1_llm_only` | `canonical_fact` | `'forecast_expectation'}` | {'class': 'forecast_status', 'text': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 18/0830Z NO VA EXP |
| `cand-cd2a63c36777cda2` | `S1_llm_only` | `canonical_fact` | `'has_advisory_datetime'}` | {'class': 'datetime_utc', 'text': '20260517/2057Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260517/2057Z |
| `cand-cf17250c9ee11442` | `S1_llm_only` | `canonical_fact` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/1430Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 18/1430Z NO VA EXP |
| `cand-e0984ab5e2d31982` | `S1_llm_only` | `canonical_fact` | `'source_elevation_is'}` | {'class': 'elevation', 'text': '11686 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-edc6c0a672b53c5e` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 71 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-fb4c6cd04f04f2d4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-fb60087f9c791397` | `S1_llm_only` | `canonical_fact` | `'may_continue'}` | {'class': 'activity_continuation', 'text': 'CONT.'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
