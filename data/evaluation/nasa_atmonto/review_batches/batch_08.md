# NASA ATMONTO Gold Review batch_08

- Samples: `ATCSCC-GOLD-071` to `ATCSCC-GOLD-080`
- Records: 10
- Candidate clusters: 198

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-071 / 2026-05-19:064

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=64
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 13

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/1900 - 20/0200 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 191721-200230 SIGNATURE: 26/05/19 17:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-16ec49ccdb479e65` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_airport_delay_event_at` | EWR airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-1c7322638390caed` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T17:21:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 17:21 |
| `cand-3b3302e3234aa6b2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `occur_during` | periods of compacted demand | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DURING PERIODS OF COMPACTED DEMAND |
| `cand-5b4ed8a70ba376a9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_constrained_facility` | ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-75a5b50019218746` | `S1_llm_only` | `freeform_or_unmapped_fact` | `gives_effective_time_window` | 191721-200230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191721-200230 |
| `cand-76cc9a52b41dfd26` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 64 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-a854ba84542c09a9` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 64, "atm:controlledNASelement": [{"label": "Newark Airport", "type": "nas:Airport"}], "atm:effectiveEndTime": "2026-05-20T02:30:00", "... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-b158226f5f9defbd` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191721-200230 |
| `cand-b2d3c792f1bae106` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect_arrival_delays_or_airborne_holding_into` | Newark Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT |
| `cand-ba3dc218e5130a46` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T17:21:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191721-200230 |
| `cand-be215412d92e2343` | `S1_llm_only` | `freeform_or_unmapped_fact` | `have_maximum_duration_of` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OF UP TO 30 MINUTES |
| `cand-f6680263477275da` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 64, "atm:controlledNASelement": [{"label": "Newark Airport", "type": "nas:Airport"}], "atm:effectiveEndTime": "2026-05-20T02:30:00", "... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-f9ae84e5e9fc4294` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_updates_will_follow_if_necessary` | updates will follow if necessary | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |

## ATCSCC-GOLD-072 / 2026-05-17:065

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=65
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 172012-180330 SIGNATURE: 26/05/17 20:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-076553c9a926c0cd` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | REPLACES / EXTENDS ADVZY 016; USERS SHOULD FUEL ACCORDINGLY. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-088d4927391412cc` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `implementationStatus` | FYI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-1a79b5de6f2a2bf1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'revision_relation'}` | {'label': 'Advisory 016', 'type': 'advisory_notice'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES / EXTENDS ADVZY 016*** |
| `cand-26e8483621e8693a` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 65, "atm:controlledNASelement": [{"evidence_text": "CONSTRAINED FACILITIES: ZAU", "label": "ZAU", "type": "nas:ARTCC"}, {"evidence_tex... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |
| `cand-3d0ce52f56119feb` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `reRouteReason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-42e85615939cfaeb` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 65 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-5cac304fbe243e95` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T03:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 172012-180330 |
| `cand-7fddc742cb283aa3` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-17T20:12:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 172012-180330 |
| `cand-8ad7891c76a43826` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T03:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-8f31ba1aeee798ff` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'ZAU', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-92271c00ea9ad7cb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': 'weather', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-a3525d075d9183c3` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T20:12:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:12 |
| `cand-b16ace501ce3c2cf` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `reRouteType` | CDR | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-bf567476089f3ffd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': 'ZAU', 'type': 'air_traffic_facility'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-d3829006b1e1e1d4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'instruction'}` | {'label': 'users', 'type': 'airspace_users'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-e2a42f88570cefc6` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T20:12:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-ee2f3b5264775b9b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'time_window_relation'}` | {'label': '17/1130 - 18/0300', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 17/1130 - 18/0300 |

## ATCSCC-GOLD-073 / 2026-05-20:006

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=6
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 11735 / 587 / 170 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 15134 / 662 / 219 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION COMMENTS: EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-14e7b2827f8319b4` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:20:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-259793c5d6666a34` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_new_total_maximum_average_delays'}` | {'class': 'delay_measurement', 'label': '15134 / 662 / 219'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 15134 / 662 / 219 |
| `cand-3add51326b769b6c` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | DFW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z DEP FACILITIES INC... |
| `cand-50f7b778c58ecec9` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-59fde377b7696bdd` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T00:21:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:21 |
| `cand-64a662982098bcf0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'specifies_element_type'}` | {'class': 'element_type', 'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-64e06df212e412a3` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-66b047097b5d59bc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_probability_of_extension'}` | {'class': 'extension_probability', 'label': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-6a3958ba12a22702` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_ground_stop_period'}` | {'class': 'time_interval', 'label': '20/0000Z - 20/0115Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-6c0157f4b34cc93c` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-6cd14c9d0f52abb7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_impacting_condition'}` | {'class': 'impacting_condition', 'label': 'RWY-TAXI / CONSTRUCTION'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION |
| `cand-6db5930eafc8ee45` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DFW | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DFW |
| `cand-6ebd8734fffec424` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'facility_group', 'label': 'ZHU ZFW ZKC ZME ZAB'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-8e0999434239456a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_cumulative_program_period'}` | {'class': 'time_interval', 'label': '19/2100Z - 20/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z |
| `cand-9035a37f0b01ae96` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'gives_effective_time_window'}` | {'class': 'effective_time_window', 'label': '200020-200215'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200020-200215 |
| `cand-92dd87c0e2790ed9` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z", "value": "DFW"}... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-b0ce4d609e90614f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_previous_total_maximum_average_delays'}` | {'class': 'delay_measurement', 'label': '11735 / 587 / 170'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 11735 / 587 / 170 |
| `cand-da8b94d887897753` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 6 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP |
| `cand-e493da22e5c33d1d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names_controlled_element'}` | {'class': 'controlled_element', 'label': 'DFW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DFW |

## ATCSCC-GOLD-074 / 2026-05-14:073

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=73
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 141857 WSI DDS:141858 VA ADVISORY DTG: 20260514/1857Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/562 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: FRQ VA EMS OBS VA DTG: 14/1830Z OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 FCST VA CLD +18HR: 15/1230Z SFC/F...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-077f48732ba2d76c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_volcanic_ash_emissions_observed_in` | sat and webcam | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: FRQ VA EMS OBSD IN SAT AND WEBCAM. |
| `cand-0cf80ac3c40d1460` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |
| `cand-1ca28b44f5e1e135` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_time` | 15/1230Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |
| `cand-1e4c3833769dd388` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reported_polygon` | N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-20f0e3230335075f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_time` | 15/0630Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-2fad25f8b29a535f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_eruption_details` | FRQ VA EMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: FRQ VA EMS |
| `cand-480e91b0353ba1ea` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_ash_clouds_disperse_slowly_and_reach_distance` | appx 8 NM fm summit | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA CLDS SLOWLY DISPERSED W REACHING APPX 8 NM FM SUMMIT. |
| `cand-4fa02fd2109ff9d1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-538593ce42b48e7a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_forecast_polygon` | N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-549e22508861b05f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_source_elevation` | 12346 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-5706a83ee18c0d22` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-582378f950c1f1ac` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_forecast_winds` | SW AND W WINDS THRU T+18HRS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDL FCST SW AND W WINDS THRU T+18HRS. |
| `cand-5aef29c501c088f6` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 73 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-5da6c44e39d5ecbf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_volcano` | FUEGO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-65c5861cd62cc3c9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_position` | N1428 W09052 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-672c17fecfe01077` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_forecast_polygon` | N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |
| `cand-8a0f979f1f6be1a8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_identifier` | ATCSCC ADVZY 073 DCC 05/14/2026 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-aedf72ba9672fb97` | `S1_llm_only` | `freeform_or_unmapped_fact` | `references_information_sources` | GOES-19, WEBCAM, NWP MODELS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. |
| `cand-c1adee25cd9a2142` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observation_time` | 14/1830Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 14/1830Z |
| `cand-c7778ff2ad510115` | `S1_llm_only` | `freeform_or_unmapped_fact` | `located_in_area` | GUATEMALA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-dafe204835e64179` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_forecast_polygon` | N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-ddb667efef17ffc1` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-dffe0a8225c2ea06` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO", "value": 73}], "atm:effectiveEndTime": [{"evi... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-e1b83f87074ccf3c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-e336d650ccb3dd29` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_event_type` | volcanic activity bulletin | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-e8ac9c0407669439` | `S1_llm_only` | `freeform_or_unmapped_fact` | `movement_direction_and_speed` | W 5KT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-e98731719a55f7ba` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T18:57:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 18:59 |
| `cand-f34c3d06e78fe7ec` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-f4eaa9b314269497` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_time` | 15/0030Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |

## ATCSCC-GOLD-075 / 2026-05-18:119

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=119
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 20

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE MESSAGE: FVXX22 KNES 182009 WSI DDS:182010 VA ADVISORY DTG: 20260518/2009Z VAAC: WASHINGTON VOLCANO: PURACE 351060 PSN: N0219 W07624 AREA: COLOMBIA SOURCE ELEV: 15256 FT AMSL ADVISORY NR: 2026/083 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: PSBL VA EMS EST VA DTG: 18/1940Z EST VA CLD: SFC/FL180 N0225 W07629 - N0219 W07623 - N0219 W07623 - N0223 W07632 - N0225 W07629 MOV NW 20KT FCST VA CLD +6HR: 19/0130Z SFC/FL180 N0226 W07629 - N0219 W07623 - N0219 W07624 - N0223 W07632 - N0226 W07629 FCST VA CLD +12HR: 19/0730Z NO VA EXP FCST VA CLD +18HR: 19/1330Z NO VA EXP RMK: VA NOT DETECTED IN STLT IMG. VA EMS MAY CONT. MDL GUIDANCE SUGGESTS...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0010ad2874a69a66` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-19eda15dbf3e407e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'movement speed'}` | {'label': '20KT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 20KT |
| `cand-2f3a8405cfad7416` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'located in area'}` | {'label': 'COLOMBIA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: COLOMBIA |
| `cand-4216b812829cb4c9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'advisory number'}` | {'label': '2026/083'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/083 |
| `cand-431985c61c81391f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has advisory title'}` | {'label': 'VOLCANIC ACTIVITY BULLETIN - PURACE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-485731146ed8c8a2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports volcano'}` | {'label': 'PURACE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: PURACE 351060 |
| `cand-4eaefd6bd96610fd` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T20:09:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:10 |
| `cand-519647f9a7c57e03` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'may continue'}` | {'label': 'CONT.'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
| `cand-8058aa76034755ff` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'did not detect volcanic ash'}` | {'label': 'VA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED IN STLT IMG. |
| `cand-8905281493295ada` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 119 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-8bda81516171d93a` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-8f9b32e73d562197` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'source elevation'}` | {'label': '15256 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 15256 FT AMSL |
| `cand-921e377a74c94722` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'suggests movement through'}` | {'label': 'NW MVMT THRU T+6'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MDL GUIDANCE SUGGESTS NW MVMT THRU T+6. |
| `cand-937e5401eae171ff` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 119, "atm:initiativeComments": "VOLCANIC ACTIVITY BULLETIN - PURACE"} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-943018f3c97c1d22` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast status'}` | {'label': 'SFC/FL180'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/0130Z SFC/FL180 |
| `cand-ac3a6c0a89921f7a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is'}` | {'label': 'LOW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST CONFIDENCE LOW. |
| `cand-c9373f46809cea04` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated ash cloud top and base'}` | {'label': 'SFC/FL180'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: PSBL VA EMS EST VA DTG: 18/1940Z EST VA CLD: SFC/FL180 |
| `cand-cc2a82011f8f2678` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast status'}` | {'label': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 19/1330Z NO VA EXP |
| `cand-d370dd1c6b644869` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast status'}` | {'label': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/0730Z NO VA EXP |
| `cand-e32c80196ce11d72` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'moves toward'}` | {'label': 'NW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 20KT |

## ATCSCC-GOLD-076 / 2026-05-20:013

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=13
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 15

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00ef4f197dc67a6d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names_controlled_element'}` | {'label': 'ORD ELEMENT', 'type': 'controlled_element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-163645cc55da5397` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 13 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX |
| `cand-1e25ea8af07c4c4e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_ground_stop_cancellation_period'}` | {'label': '20/0044Z - 20/0548Z', 'type': 'time_period'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-27aad1bd07cb5734` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'was_signed_at'}` | {'label': '26/05/20 00:46', 'type': 'signature_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 00:46 |
| `cand-2d45d3c1c1a934d4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_effective_time'}` | {'label': '200045-200648', 'type': 'effective_time_range'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200045-200648 |
| `cand-3af5001987f775ab` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-47b4f4bde23e8647` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_advisory_identifier'}` | {'label': 'ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX', 'type': 'advisory_identifier'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX |
| `cand-4ba387b0357a9c72` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: ORD", "value": "ORD"}], "atm:extensionProbability": [{"evidence_text": "GS CNX", "value": "NONE... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-598efd10b71cf028` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: ORD ELEMENT TYPE: APT", "value": "ORD"}], "atm:effectiveEndTime": [{"evidence_text": "EFFECTIVE... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-66baa09eac3ed068` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_ground_stop_cancellation_time'}` | {'label': '0044Z', 'type': 'time_value'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-6939c5284c8e72d5` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-78970ed82da97f44` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T06:48:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-8501d2a945dec055` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_element_type'}` | {'label': 'APT ADL', 'type': 'element_type'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-bedbf9754a65c364` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T00:46:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:46 |
| `cand-eee7f7d4cab1b065` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |

## ATCSCC-GOLD-077 / 2026-05-19:001

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=1
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL MESSAGE: FVXX24 KNES 190010 WSI DDS:190011 VA ADVISORY DTG: 20260519/0010Z VAAC: WASHINGTON VOLCANO: POPOCATEPETL 341090 PSN: N1901 W09837 AREA: MEXICO SOURCE ELEV: 17693 FT AMSL ADVISORY NR: 2026/195 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: OCNL VA EMS EST VA DTG: 18/2356Z EST VA CLD: SFC/FL220 N1911 W09828 - N1909 W09825 - N1901 W09837 - N1901 W09837 - N1911 W09828 MOV NE 15KT FCST VA CLD +6HR: 19/0600Z SFC/FL220 N1911 W09826 - N1908 W09824 - N1901 W09837 - N1901 W09837 - N1911 W09826 FCST VA CLD +12HR: 19/1200Z NO VA EXP FCST VA CLD +18HR: 19/1800Z NO VA EXP RMK: VA NOT DETECTED IN STLT IMG. VA EMS MAY CONT. MDL GUIDANC...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09d4f9bf04f946ee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `located_in_area` | {'label': 'Mexico', 'type': 'geographic_area'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: MEXICO |
| `cand-0bce3eb4a2e7939d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_continue` | {'label': 'Yes', 'type': 'continuation_status'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
| `cand-0ea038b42f0139b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `eruption_details_state` | {'label': 'Occasional volcanic ash emissions', 'type': 'eruption_detail'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: OCNL VA EMS |
| `cand-13afaf5a7e7f79f8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_topic` | {'label': 'Volcanic activity bulletin for Popocatepetl', 'type': 'bulletin_topic'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-1a76c252da8846ef` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-1e90c46027b5bd54` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-22c80add384d7e2b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_status_is` | {'label': 'No volcanic ash expected', 'type': 'forecast_status'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 19/1800Z NO VA EXP |
| `cand-2c7a683b173a1b09` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 1 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-44388b6120368f1b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_vertical_extent_is` | {'label': 'SFC/FL220', 'type': 'vertical_extent'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL220 |
| `cand-44d84715563f060d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `information_sources_include` | {'label': 'GOES-19', 'type': 'information_source'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. NWP MODELS. |
| `cand-4c1d49d6e60e4163` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-19T00:11:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 00:11 |
| `cand-593b27f5d8617962` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_number` | {'label': '2026/195', 'type': 'advisory_number'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/195 |
| `cand-74d6d3822f295a74` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 1 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-7abce6f26df3630c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_identifier` | {'label': 'ATCSCC ADVZY 001 DCC 05/19/2026', 'type': 'advisory_identifier'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-841ec3e125a8c53b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_status_is` | {'label': 'No volcanic ash expected', 'type': 'forecast_status'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/1200Z NO VA EXP |
| `cand-88ca64d174f7f54f` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T00:10:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 00:11 |
| `cand-8d3142a074c1ea43` | `S1_llm_only` | `freeform_or_unmapped_fact` | `source_elevation_is` | {'label': '17693 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 17693 FT AMSL |
| `cand-913f68a85c686b94` | `S1_llm_only` | `freeform_or_unmapped_fact` | `moves_toward` | {'label': 'NE', 'type': 'direction'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 15KT |
| `cand-957b310ccafb7952` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-95ec0e491913d04a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observation_result_is` | {'label': 'Volcanic ash not detected', 'type': 'observation_result'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: VA NOT DETECTED IN STLT IMG. |
| `cand-af825d17445e9086` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL | `{"rejected_schema": 2}` | `{"unknown_fact_type": 2, "unknown_subject_class": 2}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-bc0f1e3d5af90495` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_time_is` | {'label': '19/0600Z', 'type': 'time_expression'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/0600Z SFC/FL220 N1911 W09826 - N1908 W09824 - N1901 W09837 - N1901 W09837 - N1911 W09826 |
| `cand-bd296565d0a71b28` | `S1_llm_only` | `freeform_or_unmapped_fact` | `information_sources_include` | {'label': 'NWP models', 'type': 'information_source'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. NWP MODELS. |
| `cand-bfe0af0d95eb0676` | `S1_llm_only` | `freeform_or_unmapped_fact` | `suggests_movement_toward` | {'label': 'NE through T+6', 'type': 'movement_prediction'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MDL GUIDANCE SUGGESTS NE MVMT THRU T+6. |
| `cand-d687d54078255502` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-f0d08e9c6c055f62` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_time_is` | {'label': '18/2356Z', 'type': 'time_expression'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 18/2356Z |
| `cand-f28e75bc30b25124` | `S1_llm_only` | `freeform_or_unmapped_fact` | `movement_speed_is` | {'label': '15KT', 'type': 'speed'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 15KT |
| `cand-f3ef2a6a05f0b6d5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_date_time` | {'label': '20260519/0010Z', 'type': 'advisory_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260519/0010Z |

## ATCSCC-GOLD-078 / 2026-05-20:026

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=26
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 22

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 200158 WSI DDS:200159 VA ADVISORY DTG: 20260520/0158Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/584 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 20/0140Z EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 MOV SW 10KT FCST VA CLD +6HR: 20/0730Z SFC/FL150 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 FCST VA CLD +18HR: 20/1930Z SFC/FL1...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0841747437f1ca9f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-0a68dd55dbaa6dff` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-1ca6b0533f551ca7` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T01:58:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 02:00 |
| `cand-1f7e49fb2a07e789` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_vertical_extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 |
| `cand-239f6d4fd3f80d0d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast_change` | No change forecast for next 18 hours | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-23b2dec69c3f1ccb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `not_detected_by` | Satellite due to weather clouds in summit area | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-32b08ff346c31497` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_region` | Guatemala | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-3a1fa3001d91f192` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_eruption_details` | Ongoing | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING |
| `cand-5964174aaffc1cdc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_time_of_detection` | 20/0140Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 20/0140Z |
| `cand-83f71483dd9fc06c` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 26 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-8859dc9329d88bae` | `S1_llm_only` | `freeform_or_unmapped_fact` | `likely_to_continue` | Likely continue given recent activity | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-955539f35eead470` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 26 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-a9343ccf4ee8846a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-20T02:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 02:00 |
| `cand-aa60f02c89ef3cf2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_vertical_extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/1930Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09052 |
| `cand-abaa368ca28ddb80` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-af97f08e3039a3a4` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-20T20:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-b3bb130b79d0eacc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_topic` | Volcanic Activity Bulletin - Fuego | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-ba8f25e8828ccc21` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/0730Z SFC/FL150 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 |
| `cand-becd0295d5efc36b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_vertical_extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 |
| `cand-c78e9f11cf9d8717` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-ddf2af879e65d11a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_source_elevation` | 12346 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-fc8684d1c45c58c6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `movement_direction_and_speed` | SW 10KT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |

## ATCSCC-GOLD-079 / 2026-05-15:051

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=51
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 16

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 15/1300 - 15/2000 CONSTRAINED FACILITIES: ZMA ZNY ***REPLACES ADVZY 049*** *L453/L455 END TIME EXTENDED* *L451 CONSTRAINED FACILITY MODIFIED* ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. EFFECTIVE TIME: 151735-152030 SIGNATURE: 26/05/15 17:35 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-2213a50a5ec64627` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 51, "atm:implementationStatus": "RQD", "atm:issuedTime": "2026-05-15T17:35:00Z", "atm:reRouteReason": "WEATHER", "atm:reRouteType": "R... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-32dc74183fb7aecc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should file alternate routing` | alternate routing | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-37bcc66da6de2c1e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are closed due to thunderstorms` | closure | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. |
| `cand-457f7be7e8e49fbf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is` | 151735-152030 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151735-152030 |
| `cand-47d81a3340708925` | `S1_llm_only` | `freeform_or_unmapped_fact` | `constrained facility modified` | modified constrained facility | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *L451 CONSTRAINED FACILITY MODIFIED* |
| `cand-4cbf885c9a65fd4b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is closed due to thunderstorms` | closure | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-6913f3bf230a6f30` | `S0_rule_only` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | _RQD |
| `cand-79e9f3bda03ef3fc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `end time extended` | extended end time | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *L453/L455 END TIME EXTENDED* |
| `cand-83293984f016a839` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151735-152030 |
| `cand-9850013492354f96` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 51, "atm:effectiveEndTime": "2026-05-15T20:30:00Z", "atm:effectiveStartTime": "2026-05-15T17:35:00Z", "atm:implementationStatus": "RQD... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-9de072510e4254ef` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T17:35:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151735-152030 |
| `cand-a0dcc7cd9a5333f9` | `S2_llm_schema_slice` | `property_bundle` | `controlledNASelement` | {"atm:controlledNASelement": [{"label": "L453", "type": "nas:AirspaceRoute"}, {"label": "L455", "type": "nas:AirspaceRoute"}, {"label": "L451", "type": "nas:... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-a23bd29d936030ce` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T17:35:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 17:35 |
| `cand-b0906e73d5bff992` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is constrained to` | 15/1300 - 15/2000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 15/1300 - 15/2000 |
| `cand-c3cf25ba41bf7a7a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `replaces` | ADVZY 049 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES ADVZY 049*** |
| `cand-f26f1cecc4b8bc3b` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 51 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |

## ATCSCC-GOLD-080 / 2026-05-18:148

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=148
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02451bebfb7c2c4f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'element_type'}` | {'label': 'APT ADL', 'type': 'element_type_value'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-06f38ba189886a45` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T22:41:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182241-190150 |
| `cand-092df3185458f341` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T22:41:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 22:41 |
| `cand-27388649f1e50743` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T22:36:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
| `cand-2ba2272b4c90dd9d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'control_element'}` | {'label': 'BNA', 'type': 'airport_element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-4ead146520b970a3` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-565ade8d349f8438` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'status_change'}` | {'label': 'GS CNX', 'type': 'operation_status'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-5bf4ec9c48b8e0ae` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | GS CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: |
| `cand-648b05addaf018ec` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-67ca64df3bc1d7b0` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T01:50:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182241-190150 |
| `cand-7837eb72a2200a41` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'headline'}` | {'label': 'ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX', 'type': 'advisory_headline'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX |
| `cand-8bb832555c778f66` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'time_interval'}` | {'label': '182241-190150', 'type': 'effective_time_range'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182241-190150 |
| `cand-a01ca5949b96b8ab` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'BNA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: |
| `cand-a484293829491708` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'time_interval'}` | {'label': '18/2236Z - 19/0050Z', 'type': 'time_period'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 18/2236Z - 19/0050Z |
| `cand-b8a3b529351002a4` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T22:41:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 22:41 |
| `cand-d1370d2225594222` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 148 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX |
| `cand-de703d0c162814cc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'time'}` | {'label': '2236Z', 'type': 'zulu_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2236Z |
| `cand-f3d37f598c8371ec` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'BNA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
| `cand-f4bab77e4c9da103` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-19T00:50:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
