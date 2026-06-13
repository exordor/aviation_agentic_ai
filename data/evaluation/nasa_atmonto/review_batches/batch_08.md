# NASA ATMONTO Gold Review batch_08

- Samples: `ATCSCC-GOLD-071` to `ATCSCC-GOLD-080`
- Records: 10
- Candidate clusters: 251

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-071 / 2026-05-19:064

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=64
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/1900 - 20/0200 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 191721-200230 SIGNATURE: 26/05/19 17:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b6f686876c34bec` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T17:21:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-16442a20053f4ab7` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:EWR | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-1ad6df11ae7eabe8` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | Newark Airport | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-1c7322638390caed` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T17:21:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 17:21 |
| `cand-448c8f20be23a401` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-54006c12e1482db6` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-57121d971a7872cc` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T17:21:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-5e57a2a816cffc0d` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | volume | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-684f533ff555f3e0` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 64 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-767d252d0fa6a790` | `S1_llm_only` | `canonical_fact` | `names_constrained_facility` | ZNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-76cc9a52b41dfd26` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 64 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-79c45a0168409193` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-81658e9ddcbff1e2` | `S1_llm_only` | `canonical_fact` | `have_maximum_duration_of` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OF UP TO 30 MINUTES |
| `cand-969e80405bf0a315` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T17:21:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-a03c4baa5ce4934f` | `S1_llm_only` | `canonical_fact` | `states_updates_will_follow_if_necessary` | updates will follow if necessary | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-b158226f5f9defbd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191721-200230 |
| `cand-b5b37cbe2b9e10ca` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | Newark Airport | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-b5c551e652126b58` | `S1_llm_only` | `canonical_fact` | `can_expect_arrival_delays_or_airborne_holding_into` | Newark Airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT |
| `cand-ba3dc218e5130a46` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T17:21:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191721-200230 |
| `cand-c7c95258210da9cc` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T17:21:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-d55c3297e05cca71` | `S1_llm_only` | `canonical_fact` | `gives_effective_time_window` | 191721-200230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191721-200230 |
| `cand-e0ebb0c7643487b4` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-e2a144eb55430868` | `S1_llm_only` | `canonical_fact` | `identifies_airport_delay_event_at` | EWR airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-eac01ac6c89c14c1` | `S1_llm_only` | `canonical_fact` | `occur_during` | periods of compacted demand | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DURING PERIODS OF COMPACTED DEMAND |
| `cand-eee17d730d4c4995` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EWR AIRPORT ARRIVAL DELAYS | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |

## ATCSCC-GOLD-072 / 2026-05-17:065

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=65
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 172012-180330 SIGNATURE: 26/05/17 20:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0836bb48ae941599` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T17:20:12Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |
| `cand-0bb0125a03fbbbcc` | `S1_llm_only` | `canonical_fact` | `'revision_relation'}` | {'label': 'Advisory 016', 'type': 'advisory_notice'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES / EXTENDS ADVZY 016*** |
| `cand-15ad88bebac63e88` | `S1_llm_only` | `canonical_fact` | `'time_window_relation'}` | {'label': '17/1130 - 18/0300', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 17/1130 - 18/0300 |
| `cand-21cfea67cbed7452` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteReason` | WEATHER | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-23b50ba4dc81e752` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': 'weather', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-24a3bf6042403447` | `S1_llm_only` | `canonical_fact` | `'instruction'}` | {'label': 'users', 'type': 'airspace_users'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-2eca25b9000d6888` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T03:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-39849942b7010605` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | REPLACES / EXTENDS ADVZY 016; USERS SHOULD FUEL ACCORDINGLY. | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-42e85615939cfaeb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 65 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-6e056cf7a018cbb0` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ORD | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-7f9f6f2e67b5491d` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCOR... | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |
| `cand-879f4f1180835934` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T03:03:30Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |
| `cand-8ad7891c76a43826` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T03:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-8d2e5d2e319a1e2c` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |
| `cand-8f27da119c90b034` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 65 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |
| `cand-92c263e59792f059` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': 'ZAU', 'type': 'air_traffic_facility'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-99cd03cfa1c5c9a1` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | FYI | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-a3525d075d9183c3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-17T20:12:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:12 |
| `cand-a41dd49d06c4aafa` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 65 | `{"repaired_accepted": 1}` | `{}` | ***REPLACES / EXTENDS ADVZY 016*** |
| `cand-a8102388957c1dc3` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteType` | CDR | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-ac83650d3c94de8a` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZAU | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZAU |
| `cand-ad091a658aedd71b` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |
| `cand-c4979921fb96e833` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-cc26ce8be61bff4a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T20:12:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-e2a42f88570cefc6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T20:12:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-e71777b347fe543f` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | MDW | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-fc6b0f29afb0d6cc` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | CDR | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACC... |

## ATCSCC-GOLD-073 / 2026-05-20:006

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=6
- Candidate class: `GroundStopTMI`
- Current status: `reviewed`
- Candidate clusters: 32

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 11735 / 587 / 170 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 15134 / 662 / 219 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION COMMENTS: EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b044c4876578a80` | `S1_llm_only` | `canonical_fact` | `'states_probability_of_extension'}` | {'class': 'extension_probability', 'label': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-0b2d405223ca8ca0` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:15:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-0ffb3bd1152b8351` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | runway | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION COMMENTS: |
| `cand-14e7b2827f8319b4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:20:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-26202b36718cb883` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | DFW | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-2e46c09b43eceffa` | `S1_llm_only` | `canonical_fact` | `'reports_new_total_maximum_average_delays'}` | {'class': 'delay_measurement', 'label': '15134 / 662 / 219'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 15134 / 662 / 219 |
| `cand-3150f5e1f4ad0359` | `S1_llm_only` | `canonical_fact` | `'names_controlled_element'}` | {'class': 'controlled_element', 'label': 'DFW'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DFW |
| `cand-37b85ccd388751fa` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | RWY-TAXI / CONSTRUCTION | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION COMMENTS: |
| `cand-50f7b778c58ecec9` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-59fde377b7696bdd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T00:21:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:21 |
| `cand-5fa531f35b4ac3a9` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-64e06df212e412a3` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:15:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-66e5d080f875473a` | `S1_llm_only` | `canonical_fact` | `'reports_previous_total_maximum_average_delays'}` | {'class': 'delay_measurement', 'label': '11735 / 587 / 170'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 11735 / 587 / 170 |
| `cand-6c0157f4b34cc93c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-6db5930eafc8ee45` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DFW | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DFW |
| `cand-73ec9cc8a93ad35a` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | DFW | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DFW |
| `cand-7e7546cee392c110` | `S1_llm_only` | `canonical_fact` | `'states_cumulative_program_period'}` | {'class': 'time_interval', 'label': '19/2100Z - 20/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z |
| `cand-890cd8cd862db4f1` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-aedb827cc874337d` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-aee06c0e54467e2a` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | rwy-taxi / construction | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION |
| `cand-c6b22601be6b7f74` | `S1_llm_only` | `canonical_fact` | `'gives_effective_time_window'}` | {'class': 'effective_time_window', 'label': '200020-200215'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200020-200215 |
| `cand-ca1f4f1898b0df87` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z DEP FACILITIES INC... |
| `cand-d02dfecd4f137bb3` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-d107f2ae1f4635b6` | `S1_llm_only` | `canonical_fact` | `'identifies_impacting_condition'}` | {'class': 'impacting_condition', 'label': 'RWY-TAXI / CONSTRUCTION'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION |
| `cand-d3534ec8ecc0467f` | `S1_llm_only` | `canonical_fact` | `'announces_ground_stop_period'}` | {'class': 'time_interval', 'label': '20/0000Z - 20/0115Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-d98908e0e1a56600` | `S2_llm_schema_slice` | `canonical_fact` | `departureScope` | {"class": "atm:AirportSpec", "properties": {"atm:withinARTCC": [{"evidence_text": "DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB", "value": "nas:ART... | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-da8b94d887897753` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 6 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP |
| `cand-dc1b2540226e5186` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAB | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-dd10f2b507df027f` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-f285afa06fcdaf40` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-f6a9fbb335086b86` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'facility_group', 'label': 'ZHU ZFW ZKC ZME ZAB'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-f8e3e98b201dccbd` | `S1_llm_only` | `canonical_fact` | `'specifies_element_type'}` | {'class': 'element_type', 'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |

## ATCSCC-GOLD-074 / 2026-05-14:073

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=73
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 32

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 141857 WSI DDS:141858 VA ADVISORY DTG: 20260514/1857Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/562 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: FRQ VA EMS OBS VA DTG: 14/1830Z OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 FCST VA CLD +18HR: 15/1230Z SFC/F...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0429a57fb256e737` | `S1_llm_only` | `canonical_fact` | `has_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-0e50e9dc8ea8c899` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T18:59:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 18:59 |
| `cand-152e8ad5f455ed54` | `S1_llm_only` | `canonical_fact` | `has_position` | N1428 W09052 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-1ab04e3383d8c8a2` | `S1_llm_only` | `canonical_fact` | `observation_time` | 14/1830Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 14/1830Z |
| `cand-1af384f0f11b4ffe` | `S1_llm_only` | `canonical_fact` | `reports_event_type` | volcanic activity bulletin | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-21498afb668a17bd` | `S1_llm_only` | `canonical_fact` | `has_forecast_polygon` | N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-236c76e780014a4f` | `S1_llm_only` | `canonical_fact` | `references_information_sources` | GOES-19, WEBCAM, NWP MODELS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. |
| `cand-2b29b06e67f919b7` | `S1_llm_only` | `canonical_fact` | `has_reported_polygon` | N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-34688e067cb56f5e` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T14:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-3b01664e72aeb0ae` | `S1_llm_only` | `canonical_fact` | `forecast_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-599d5ae2dc66fc14` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T14:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-5a811f1daea39870` | `S1_llm_only` | `canonical_fact` | `forecast_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-5aef29c501c088f6` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 73 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-5e6abcc9e6cd775b` | `S1_llm_only` | `canonical_fact` | `states_forecast_winds` | SW AND W WINDS THRU T+18HRS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDL FCST SW AND W WINDS THRU T+18HRS. |
| `cand-6348a208e23a9f78` | `S1_llm_only` | `canonical_fact` | `states_ash_clouds_disperse_slowly_and_reach_distance` | appx 8 NM fm summit | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA CLDS SLOWLY DISPERSED W REACHING APPX 8 NM FM SUMMIT. |
| `cand-66f94cda0934a8bb` | `S1_llm_only` | `canonical_fact` | `names_volcano` | FUEGO | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-7616c8f0d5009365` | `S1_llm_only` | `canonical_fact` | `has_forecast_polygon` | N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-7815a5a347130a97` | `S1_llm_only` | `canonical_fact` | `forecast_time` | 15/1230Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |
| `cand-a030ff50aef3cdf0` | `S1_llm_only` | `canonical_fact` | `has_advisory_identifier` | ATCSCC ADVZY 073 DCC 05/14/2026 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-b34de0768593a96c` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-b719bf763f0c498d` | `S1_llm_only` | `canonical_fact` | `has_eruption_details` | FRQ VA EMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: FRQ VA EMS |
| `cand-ba5122c0db00cbb7` | `S1_llm_only` | `canonical_fact` | `located_in_area` | GUATEMALA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-bb9daa9b906ee8d7` | `S1_llm_only` | `canonical_fact` | `forecast_time` | 15/0030Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-bd9131016e75ddab` | `S1_llm_only` | `canonical_fact` | `movement_direction_and_speed` | W 5KT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-bef5fc5d2bed4ac0` | `S1_llm_only` | `canonical_fact` | `has_source_elevation` | 12346 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-c5512d00622ad7db` | `S1_llm_only` | `canonical_fact` | `has_forecast_polygon` | N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |
| `cand-ce500204dde4bb58` | `S1_llm_only` | `canonical_fact` | `forecast_time` | 15/0630Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-ddb667efef17ffc1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-e04fd891011ab2d8` | `S1_llm_only` | `canonical_fact` | `states_volcanic_ash_emissions_observed_in` | sat and webcam | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: FRQ VA EMS OBSD IN SAT AND WEBCAM. |
| `cand-e98731719a55f7ba` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-14T18:57:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 18:59 |
| `cand-f34c3d06e78fe7ec` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-f7f2e52dbefe9338` | `S1_llm_only` | `canonical_fact` | `forecast_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |

## ATCSCC-GOLD-075 / 2026-05-18:119

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=119
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 21

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE MESSAGE: FVXX22 KNES 182009 WSI DDS:182010 VA ADVISORY DTG: 20260518/2009Z VAAC: WASHINGTON VOLCANO: PURACE 351060 PSN: N0219 W07624 AREA: COLOMBIA SOURCE ELEV: 15256 FT AMSL ADVISORY NR: 2026/083 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: PSBL VA EMS EST VA DTG: 18/1940Z EST VA CLD: SFC/FL180 N0225 W07629 - N0219 W07623 - N0219 W07623 - N0223 W07632 - N0225 W07629 MOV NW 20KT FCST VA CLD +6HR: 19/0130Z SFC/FL180 N0226 W07629 - N0219 W07623 - N0219 W07624 - N0223 W07632 - N0226 W07629 FCST VA CLD +12HR: 19/0730Z NO VA EXP FCST VA CLD +18HR: 19/1330Z NO VA EXP RMK: VA NOT DETECTED IN STLT IMG. VA EMS MAY CONT. MDL GUIDANCE SUGGESTS...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0010ad2874a69a66` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-00c3a173919e8609` | `S1_llm_only` | `canonical_fact` | `'did not detect volcanic ash'}` | {'label': 'VA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED IN STLT IMG. |
| `cand-1c19d9d0596b5f3e` | `S1_llm_only` | `canonical_fact` | `'forecast status'}` | {'label': 'SFC/FL180'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/0130Z SFC/FL180 |
| `cand-39cc59e3e8310259` | `S1_llm_only` | `canonical_fact` | `'advisory number'}` | {'label': '2026/083'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/083 |
| `cand-4eaefd6bd96610fd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T20:09:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:10 |
| `cand-4ec4c0d9aea78d3f` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 119 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/083 |
| `cand-54b5c633c4c7955d` | `S1_llm_only` | `canonical_fact` | `'may continue'}` | {'label': 'CONT.'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
| `cand-59fa28089b3303df` | `S1_llm_only` | `canonical_fact` | `'source elevation'}` | {'label': '15256 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 15256 FT AMSL |
| `cand-6ffbf1e2edf6a2ab` | `S1_llm_only` | `canonical_fact` | `'estimated ash cloud top and base'}` | {'label': 'SFC/FL180'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: PSBL VA EMS EST VA DTG: 18/1940Z EST VA CLD: SFC/FL180 |
| `cand-81e0a657db44413c` | `S1_llm_only` | `canonical_fact` | `'is'}` | {'label': 'LOW'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST CONFIDENCE LOW. |
| `cand-86a823de1e641135` | `S1_llm_only` | `canonical_fact` | `'located in area'}` | {'label': 'COLOMBIA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: COLOMBIA |
| `cand-8905281493295ada` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 119 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-8bda81516171d93a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-a3c35652f9ed80b4` | `S1_llm_only` | `canonical_fact` | `'movement speed'}` | {'label': '20KT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 20KT |
| `cand-a9453ff053a88a68` | `S1_llm_only` | `canonical_fact` | `'forecast status'}` | {'label': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 19/1330Z NO VA EXP |
| `cand-b496478e62e8540b` | `S1_llm_only` | `canonical_fact` | `'reports volcano'}` | {'label': 'PURACE'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: PURACE 351060 |
| `cand-b71a05de1b9b0e4f` | `S1_llm_only` | `canonical_fact` | `'forecast status'}` | {'label': 'NO VA EXP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/0730Z NO VA EXP |
| `cand-d193538dfe43da22` | `S1_llm_only` | `canonical_fact` | `'has advisory title'}` | {'label': 'VOLCANIC ACTIVITY BULLETIN - PURACE'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-d5836a4cc3568acc` | `S1_llm_only` | `canonical_fact` | `'suggests movement through'}` | {'label': 'NW MVMT THRU T+6'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MDL GUIDANCE SUGGESTS NW MVMT THRU T+6. |
| `cand-e1b0219a7d467c73` | `S1_llm_only` | `canonical_fact` | `'moves toward'}` | {'label': 'NW'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 20KT |
| `cand-ebd5fbc6392186b1` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - PURACE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |

## ATCSCC-GOLD-076 / 2026-05-20:013

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=13
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08ec29af2218658b` | `S1_llm_only` | `canonical_fact` | `'names_controlled_element'}` | {'label': 'ORD ELEMENT', 'type': 'controlled_element'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-0efe226431af91e2` | `S1_llm_only` | `canonical_fact` | `'has_advisory_identifier'}` | {'label': 'ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX', 'type': 'advisory_identifier'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX |
| `cand-163645cc55da5397` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 13 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX |
| `cand-17730891bca1a550` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | ORD | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-1b2f715532a913a9` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | NONE | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 20/0044Z - 20/0548Z |
| `cand-29bd5cb368868828` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | GS CNX PERIOD: 20/0044Z - 20/0548Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 |
| `cand-3af5001987f775ab` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-3e721474c68fbf70` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:06:48Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-6939c5284c8e72d5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-73bfe796d151fa34` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T00:44:00Z | `{"repaired_accepted": 1}` | `{}` | ADL TIME: 0044Z |
| `cand-78970ed82da97f44` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T06:48:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-7b39fbc33d02d1ed` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | NONE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-818c2d7314543be4` | `S1_llm_only` | `canonical_fact` | `'states_ground_stop_cancellation_time'}` | {'label': '0044Z', 'type': 'time_value'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-9a9b1638c94d811f` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:04:45Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-9f4d2096944328ff` | `S1_llm_only` | `canonical_fact` | `'was_signed_at'}` | {'label': '26/05/20 00:46', 'type': 'signature_time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 00:46 |
| `cand-ad4d167da1930cb8` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-20T00:46:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:46 |
| `cand-adf9a8956e5029b3` | `S1_llm_only` | `canonical_fact` | `'has_effective_time'}` | {'label': '200045-200648', 'type': 'effective_time_range'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200045-200648 |
| `cand-b0bfa9c9799ac2f7` | `S1_llm_only` | `canonical_fact` | `'states_ground_stop_cancellation_period'}` | {'label': '20/0044Z - 20/0548Z', 'type': 'time_period'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-bedbf9754a65c364` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T00:46:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:46 |
| `cand-e32f92a07080a8e9` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ORD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT |
| `cand-edfe6cc56a908314` | `S1_llm_only` | `canonical_fact` | `'has_element_type'}` | {'label': 'APT ADL', 'type': 'element_type'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-eee7f7d4cab1b065` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-fc9cd34778b7511d` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | GS CNX PERIOD: 20/0044Z - 20/0548Z | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 20/0044Z - 20/0548Z |

## ATCSCC-GOLD-077 / 2026-05-19:001

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=1
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL MESSAGE: FVXX24 KNES 190010 WSI DDS:190011 VA ADVISORY DTG: 20260519/0010Z VAAC: WASHINGTON VOLCANO: POPOCATEPETL 341090 PSN: N1901 W09837 AREA: MEXICO SOURCE ELEV: 17693 FT AMSL ADVISORY NR: 2026/195 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: OCNL VA EMS EST VA DTG: 18/2356Z EST VA CLD: SFC/FL220 N1911 W09828 - N1909 W09825 - N1901 W09837 - N1901 W09837 - N1911 W09828 MOV NE 15KT FCST VA CLD +6HR: 19/0600Z SFC/FL220 N1911 W09826 - N1908 W09824 - N1901 W09837 - N1901 W09837 - N1911 W09826 FCST VA CLD +12HR: 19/1200Z NO VA EXP FCST VA CLD +18HR: 19/1800Z NO VA EXP RMK: VA NOT DETECTED IN STLT IMG. VA EMS MAY CONT. MDL GUIDANC...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01135dad86d3898a` | `S1_llm_only` | `canonical_fact` | `forecast_status_is` | {'label': 'No volcanic ash expected', 'type': 'forecast_status'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 19/1800Z NO VA EXP |
| `cand-02befe81e9fafb0d` | `S1_llm_only` | `canonical_fact` | `has_advisory_date_time` | {'label': '20260519/0010Z', 'type': 'advisory_time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260519/0010Z |
| `cand-097da75ed102db97` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 1 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/195 |
| `cand-141fdab2d06be4af` | `S1_llm_only` | `canonical_fact` | `observation_result_is` | {'label': 'Volcanic ash not detected', 'type': 'observation_result'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: VA NOT DETECTED IN STLT IMG. |
| `cand-19042885bb391bc1` | `S1_llm_only` | `canonical_fact` | `movement_speed_is` | {'label': '15KT', 'type': 'speed'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 15KT |
| `cand-1e90c46027b5bd54` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-271cb418bd5158af` | `S1_llm_only` | `canonical_fact` | `has_advisory_identifier` | {'label': 'ATCSCC ADVZY 001 DCC 05/19/2026', 'type': 'advisory_identifier'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-2e50a5b90dc6c6d6` | `S1_llm_only` | `canonical_fact` | `has_topic` | {'label': 'Volcanic activity bulletin for Popocatepetl', 'type': 'bulletin_topic'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-3597279457eef4b0` | `S1_llm_only` | `canonical_fact` | `information_sources_include` | {'label': 'GOES-19', 'type': 'information_source'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. NWP MODELS. |
| `cand-67167b774eae24e0` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-74d6d3822f295a74` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 1 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-88ca64d174f7f54f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T00:10:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 00:11 |
| `cand-957b310ccafb7952` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-96f245b3cbd0ace1` | `S1_llm_only` | `canonical_fact` | `estimated_vertical_extent_is` | {'label': 'SFC/FL220', 'type': 'vertical_extent'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL220 |
| `cand-a4f0da697fba746c` | `S1_llm_only` | `canonical_fact` | `estimated_time_is` | {'label': '18/2356Z', 'type': 'time_expression'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 18/2356Z |
| `cand-ab14fe6982e53705` | `S1_llm_only` | `canonical_fact` | `suggests_movement_toward` | {'label': 'NE through T+6', 'type': 'movement_prediction'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MDL GUIDANCE SUGGESTS NE MVMT THRU T+6. |
| `cand-ab576cd3d739f196` | `S1_llm_only` | `canonical_fact` | `forecast_time_is` | {'label': '19/0600Z', 'type': 'time_expression'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/0600Z SFC/FL220 N1911 W09826 - N1908 W09824 - N1901 W09837 - N1901 W09837 - N1911 W09826 |
| `cand-b3a2cc4afbc20660` | `S1_llm_only` | `canonical_fact` | `information_sources_include` | {'label': 'NWP models', 'type': 'information_source'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. NWP MODELS. |
| `cand-c4b4967d23dbe62d` | `S1_llm_only` | `canonical_fact` | `moves_toward` | {'label': 'NE', 'type': 'direction'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 15KT |
| `cand-c9e4068af9a45397` | `S1_llm_only` | `canonical_fact` | `located_in_area` | {'label': 'Mexico', 'type': 'geographic_area'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: MEXICO |
| `cand-cd6e8e920a460b50` | `S1_llm_only` | `canonical_fact` | `may_continue` | {'label': 'Yes', 'type': 'continuation_status'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
| `cand-ce060656f2947954` | `S1_llm_only` | `canonical_fact` | `source_elevation_is` | {'label': '17693 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 17693 FT AMSL |
| `cand-d5b00f1d03babea5` | `S1_llm_only` | `canonical_fact` | `forecast_status_is` | {'label': 'No volcanic ash expected', 'type': 'forecast_status'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/1200Z NO VA EXP |
| `cand-e298beb364a9b9cc` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-ea32fc75f9dff69d` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T00:11:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 00:11 |
| `cand-eb771c8d76e8e440` | `S1_llm_only` | `canonical_fact` | `has_advisory_number` | {'label': '2026/195', 'type': 'advisory_number'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/195 |
| `cand-ed056718a192127e` | `S1_llm_only` | `canonical_fact` | `eruption_details_state` | {'label': 'Occasional volcanic ash emissions', 'type': 'eruption_detail'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: OCNL VA EMS |

## ATCSCC-GOLD-078 / 2026-05-20:026

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=26
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 21

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 200158 WSI DDS:200159 VA ADVISORY DTG: 20260520/0158Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/584 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 20/0140Z EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 MOV SW 10KT FCST VA CLD +6HR: 20/0730Z SFC/FL150 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 FCST VA CLD +18HR: 20/1930Z SFC/FL1...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0a68dd55dbaa6dff` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-176659542d76057e` | `S1_llm_only` | `canonical_fact` | `estimated_vertical_extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 |
| `cand-1ca6b0533f551ca7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T01:58:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 02:00 |
| `cand-1d51e7e709980eb4` | `S1_llm_only` | `canonical_fact` | `estimated_time_of_detection` | 20/0140Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 20/0140Z |
| `cand-420686f0e00d592d` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-46ac7814738b11e0` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T02:00:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 02:00 |
| `cand-486c0c3e4abe4e6f` | `S1_llm_only` | `canonical_fact` | `has_advisory_topic` | Volcanic Activity Bulletin - Fuego | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-7387a9faa3e4ad0e` | `S1_llm_only` | `canonical_fact` | `movement_direction_and_speed` | SW 10KT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-76382fac220c5a30` | `S1_llm_only` | `canonical_fact` | `has_advisory_region` | Guatemala | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-83f71483dd9fc06c` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 26 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-92b9278b9a69e678` | `S1_llm_only` | `canonical_fact` | `forecast_change` | No change forecast for next 18 hours | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-9c57371426f54d28` | `S1_llm_only` | `canonical_fact` | `estimated_vertical_extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/1930Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09052 |
| `cand-a40908d03115aac4` | `S1_llm_only` | `canonical_fact` | `likely_to_continue` | Likely continue given recent activity | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-a6161f8be7e72f38` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-abaa368ca28ddb80` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-b045a3fb9080889e` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T20:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-b735f72d7ea8f240` | `S1_llm_only` | `canonical_fact` | `estimated_vertical_extent` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/0730Z SFC/FL150 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 |
| `cand-bd07ff4bb2517f5d` | `S1_llm_only` | `canonical_fact` | `estimated_vertical_extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 |
| `cand-db1ec6bbb3891310` | `S1_llm_only` | `canonical_fact` | `identifies_eruption_details` | Ongoing | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING |
| `cand-e5940e801f28378c` | `S1_llm_only` | `canonical_fact` | `not_detected_by` | Satellite due to weather clouds in summit area | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-fbe5166f844e52e0` | `S1_llm_only` | `canonical_fact` | `has_source_elevation` | 12346 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |

## ATCSCC-GOLD-079 / 2026-05-15:051

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=51
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 15/1300 - 15/2000 CONSTRAINED FACILITIES: ZMA ZNY ***REPLACES ADVZY 049*** *L453/L455 END TIME EXTENDED* *L451 CONSTRAINED FACILITY MODIFIED* ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. EFFECTIVE TIME: 151735-152030 SIGNATURE: 26/05/15 17:35 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0168aaba8919839b` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | L451 | `{"repaired_accepted": 1}` | `{}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-07961a6b162661fe` | `S1_llm_only` | `canonical_fact` | `end time extended` | extended end time | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *L453/L455 END TIME EXTENDED* |
| `cand-100d593ab09283c5` | `S1_llm_only` | `canonical_fact` | `constrained facility modified` | modified constrained facility | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *L451 CONSTRAINED FACILITY MODIFIED* |
| `cand-13b01d44989c1871` | `S1_llm_only` | `canonical_fact` | `replaces` | ADVZY 049 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES ADVZY 049*** |
| `cand-1506bb818b7c753d` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteType` | ROUTE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-1be9b24ff1502d3e` | `S1_llm_only` | `canonical_fact` | `is closed due to thunderstorms` | closure | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-270f93af1d14c1d7` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-2eac6bfa141cc107` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T17:35:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-4285b224004cf0b2` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | L453/L455 END TIME EXTENDED | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-5f3173d5941335ef` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 51 | `{"repaired_accepted": 1}` | `{}` | ***REPLACES ADVZY 049*** |
| `cand-6913f3bf230a6f30` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-83293984f016a839` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151735-152030 |
| `cand-972492669025edf3` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | L453 | `{"repaired_accepted": 1}` | `{}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-9de072510e4254ef` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T17:35:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151735-152030 |
| `cand-a23bd29d936030ce` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-15T17:35:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 17:35 |
| `cand-bd2fddba03353b79` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-15T17:35:00Z | `{"repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-c3ac286e07a70400` | `S1_llm_only` | `canonical_fact` | `should file alternate routing` | alternate routing | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-c5fc66fe91796f85` | `S1_llm_only` | `canonical_fact` | `is constrained to` | 15/1300 - 15/2000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 15/1300 - 15/2000 |
| `cand-c71e79f4fd9987c1` | `S1_llm_only` | `canonical_fact` | `are closed due to thunderstorms` | closure | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. |
| `cand-cf212174f8b07378` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | L455 | `{"repaired_accepted": 1}` | `{}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-db297ea2a0eae7ef` | `S1_llm_only` | `canonical_fact` | `is` | 151735-152030 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151735-152030 |
| `cand-f04309e9fee424ce` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-f26f1cecc4b8bc3b` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 51 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-f4e7cd872a8b74b2` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteReason` | WEATHER | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |

## ATCSCC-GOLD-080 / 2026-05-18:148

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=148
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
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
| `cand-0606f89e0f9d7858` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
| `cand-06f38ba189886a45` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T22:41:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182241-190150 |
| `cand-0a0f3532b8487b1d` | `S1_llm_only` | `canonical_fact` | `'time_interval'}` | {'label': '182241-190150', 'type': 'effective_time_range'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182241-190150 |
| `cand-10e22368ce990b27` | `S1_llm_only` | `canonical_fact` | `'headline'}` | {'label': 'ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX', 'type': 'advisory_headline'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX |
| `cand-39268567ca4cc380` | `S1_llm_only` | `canonical_fact` | `'element_type'}` | {'label': 'APT ADL', 'type': 'element_type_value'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-49c2bbccc9d8e59a` | `S1_llm_only` | `canonical_fact` | `'time_interval'}` | {'label': '18/2236Z - 19/0050Z', 'type': 'time_period'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 18/2236Z - 19/0050Z |
| `cand-4ead146520b970a3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-648b05addaf018ec` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: BNA |
| `cand-67ca64df3bc1d7b0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T01:50:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182241-190150 |
| `cand-7352dc480ac48aa8` | `S1_llm_only` | `canonical_fact` | `'time'}` | {'label': '2236Z', 'type': 'zulu_time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2236Z |
| `cand-75c24b49e2185b6d` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T22:41:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 22:41 |
| `cand-7d7af8cc3455b208` | `S1_llm_only` | `canonical_fact` | `'control_element'}` | {'label': 'BNA', 'type': 'airport_element'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-aaf0ab19ace2164c` | `S1_llm_only` | `canonical_fact` | `'status_change'}` | {'label': 'GS CNX', 'type': 'operation_status'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-b8a3b529351002a4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T22:41:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 22:41 |
| `cand-c9b0da5215fed9f8` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:50:00Z | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
| `cand-cc188b9a326d7cd6` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | GS CNX | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: |
| `cand-d1370d2225594222` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 148 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX |
| `cand-daa23acfa3c60388` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T22:36:00Z | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
| `cand-ea11c95faf7ab613` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | BNA | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: |
