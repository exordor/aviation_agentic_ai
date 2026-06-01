# NASA ATMONTO Gold Review batch_04

- Samples: `ATCSCC-GOLD-031` to `ATCSCC-GOLD-040`
- Records: 10
- Candidate clusters: 312

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-031 / 2026-05-19:011

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=11
- Candidate class: `GroundStopTMI`
- Current status: `reviewed`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0409Z GROUND STOP PERIOD: 19/0400Z - 19/0515Z CUMULATIVE PROGRAM PERIOD: 18/1515Z - 19/0659Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 142 / 63 / 16 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 772 / 228 / 86 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: OTHER / OTHER COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. EFFECTIVE TIME: 190409-190615 SIGNATURE: 26/05/19 04:10 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00d9022b39f54f7a` | `S1_llm_only` | `canonical_fact` | `'is_impacted_by_condition'}` | {'class': 'impacting_condition', 'text': 'OTHER / OTHER'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-071caa168f08eef7` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-07665cf04747eedb` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T04:00:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 19/0400Z - 19/0515Z |
| `cand-0e325668358f8031` | `S1_llm_only` | `canonical_fact` | `'applies_to_control_element'}` | {'class': 'facility', 'text': 'SFO'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-18c3fde70bbbfbfc` | `S1_llm_only` | `canonical_fact` | `'has_probability_of_extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-367caffb196d2542` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-19T04:10:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/19 04:10 |
| `cand-40973cf3ec88624b` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | OTHER / OTHER | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-45a82f1214eea374` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-47cd5986d8c6c657` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T04:09:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190409-190615 |
| `cand-5adc0dbf7c5f4b90` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'facility_group', 'text': 'ZLA ZLC ZOA ZSE'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE |
| `cand-7036e6cb8c8a7bc6` | `S1_llm_only` | `canonical_fact` | `'has_comment_explaining_cause'}` | {'class': 'comment', 'text': 'DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION.'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-72d2e1a43b675c68` | `S1_llm_only` | `canonical_fact` | `'has_cumulative_program_period'}` | {'class': 'time_interval', 'text': '18/1515Z - 19/0659Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 18/1515Z - 19/0659Z |
| `cand-785d5265f8bf87ed` | `S1_llm_only` | `canonical_fact` | `'has_effective_time'}` | {'class': 'effective_time_interval', 'text': '190409-190615'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190409-190615 |
| `cand-8a9153bb3f9911c2` | `S1_llm_only` | `canonical_fact` | `'has_advisory_time'}` | {'class': 'zulu_time', 'text': '0409Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 0409Z |
| `cand-8bced49e66dcbadd` | `S1_llm_only` | `canonical_fact` | `'announces'}` | {'class': 'traffic_management_program', 'text': 'GROUND STOP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP |
| `cand-8cb93377221510d4` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-92667605cfd166b5` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. | `{"repaired_accepted": 2}` | `{}` | COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-964d9c1174043e81` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-b84d1374a2084688` | `S1_llm_only` | `canonical_fact` | `'has_control_element_type'}` | {'class': 'control_element_type', 'text': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-bc3ea3660469da1b` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T06:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190409-190615 |
| `cand-ca6448ab68c57e4c` | `S1_llm_only` | `canonical_fact` | `'previous_delays_reported_as'}` | {'class': 'delay_statistics', 'text': '142 / 63 / 16'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 142 / 63 / 16 |
| `cand-e649736ac9016213` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-eb5072224f11009a` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 11 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP |
| `cand-f4d0ff77d4bcb858` | `S1_llm_only` | `canonical_fact` | `'has_ground_stop_period'}` | {'class': 'time_interval', 'text': '19/0400Z - 19/0515Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 19/0400Z - 19/0515Z |
| `cand-fc75b7f858bb50cc` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T05:15:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 19/0400Z - 19/0515Z |
| `cand-fe4446968cc8182c` | `S1_llm_only` | `canonical_fact` | `'new_delays_reported_as'}` | {'class': 'delay_statistics', 'text': '772 / 228 / 86'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 772 / 228 / 86 |

## ATCSCC-GOLD-032 / 2026-05-20:131

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=131
- Candidate class: `GroundStopTMI`
- Current status: `reviewed`
- Candidate clusters: 30

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1957Z GROUND STOP PERIOD: 20/1947Z - 20/2130Z DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1387 / 68 / 30 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 4276 / 171 / 93 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: GROUND STOP EXTENSION. EFFECTIVE TIME: 202001-202230 SIGNATURE: 26/05/20 20:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01cba1d2d80202de` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T20:02:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 20:02 |
| `cand-0cecac67571972d3` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-0f76f643acccc6a2` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 131 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-1518fddef0e615c6` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD |
| `cand-15e8170ed2ec2143` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T22:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-285cf9794786b0e9` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 202001-202230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-34276ef6718793bd` | `S1_llm_only` | `canonical_fact` | `has_control_element` | IAD | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD |
| `cand-369e08f75f61c1d6` | `S1_llm_only` | `canonical_fact` | `has_previous_delays` | 1387 / 68 / 30 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1387 / 68 / 30 |
| `cand-39a1abda6cd9af66` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T22:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202001-202230 |
| `cand-559051b34033e226` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 131 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-574fc65e2a607b02` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | IAD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1957Z GROUND STOP PERIOD: 20/1947Z - 20/2130Z |
| `cand-582b30d1bba81ca1` | `S2_llm_schema_slice` | `canonical_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-5853ec918889485b` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | GROUND STOP EXTENSION. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: GROUND STOP EXTENSION. |
| `cand-63e8c9f983ba75e6` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | IAD | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD |
| `cand-653c7ec30a58c5ea` | `S1_llm_only` | `canonical_fact` | `describes_ground_stop_period` | 20/1947Z - 20/2130Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/1947Z - 20/2130Z |
| `cand-71d614307d685413` | `S1_llm_only` | `canonical_fact` | `includes_departure_facilities` | ZTL ZDC ZNY ZJX ZOB ZBW ZID | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-799724068c0f8b08` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-87a5344e48c1e019` | `S1_llm_only` | `canonical_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-89574b09b53466fc` | `S1_llm_only` | `canonical_fact` | `has_new_delays` | 4276 / 171 / 93 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 4276 / 171 / 93 |
| `cand-9ae972c0cb147f8a` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | GROUND STOP EXTENSION. | `{"repaired_accepted": 2}` | `{}` | COMMENTS: GROUND STOP EXTENSION. |
| `cand-9cd88ea728114406` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a363f3f25ccd48ab` | `S1_llm_only` | `canonical_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-ac02906fd37ffdf1` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-aefa9ea47d53bcda` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:01:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202001-202230 |
| `cand-b5ebc6374cde5b96` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-cfefdaf9d2e28bc5` | `S1_llm_only` | `canonical_fact` | `has_adl_time` | 1957Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADT TIME: 1957Z |
| `cand-ded5bbdc4293fe5b` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:02:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-e79119e757730bcf` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e9a9d34342e3c8e0` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T20:02:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 20:02 |
| `cand-fcc83705f4d342d9` | `S1_llm_only` | `canonical_fact` | `has_comment` | GROUND STOP EXTENSION. | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: GROUND STOP EXTENSION. |

## ATCSCC-GOLD-033 / 2026-05-18:025

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=25
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: LAS ELEMENT TYPE: APT ADL TIME: 0750Z GDP CNX PERIOD: 18/0750Z - 18/1854Z DISREGARD EDCTS FOR DEST LAS COMMENTS: EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05f87111c8268a3e` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:LAS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS ELEMENT TYPE: APT |
| `cand-1287b7646d856ce9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T07:50:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180750-181954 |
| `cand-39355363e63c8c5a` | `S1_llm_only` | `canonical_fact` | `'GDP CNX'}` | {'label': 'ground delay program cancellation', 'value': 'GDP CNX'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-419e20266cb43fe1` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | DISREGARD EDCTS FOR DEST LAS | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: EFFECTIVE TIME: 180750-181954 |
| `cand-4a1f599192a9f9b8` | `S1_llm_only` | `canonical_fact` | `'DISREGARD'}` | {'label': 'EDCTS for destination LAS', 'value': 'EDCTS FOR DEST LAS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISREGARD EDCTS FOR DEST LAS |
| `cand-4f6ea6bcb991dc93` | `S1_llm_only` | `canonical_fact` | `'GDP CNX PERIOD'}` | {'label': '18/0750Z - 18/1854Z', 'value': '18/0750Z - 18/1854Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GDP CNX PERIOD: 18/0750Z - 18/1854Z |
| `cand-544bfa3ab381e86b` | `S1_llm_only` | `canonical_fact` | `'ADL TIME'}` | {'label': '0750Z', 'value': '0750Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 0750Z |
| `cand-5595163c7baa76f1` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | LAS | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-5bccad478205a0ab` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 25 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-776f23fba42681e5` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T19:54:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-8174e1a17e317f2e` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T07:50:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-851b995f0e0ad673` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T07:50:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 07:50 |
| `cand-884241e4302debb0` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 25 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-8ff4615cf5c01a54` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T19:54:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180750-181954 |
| `cand-934208a4f24bd1ec` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: LAS |
| `cand-b2ffac2c71a6a27e` | `S1_llm_only` | `canonical_fact` | `'CTL ELEMENT'}` | {'label': 'LAS', 'value': 'LAS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS |
| `cand-e9008eccc798d66a` | `S1_llm_only` | `canonical_fact` | `'EFFECTIVE TIME'}` | {'label': '180750-181954', 'value': '180750-181954'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-f425d44c55b948ff` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-f8d8bc998262f46d` | `S1_llm_only` | `canonical_fact` | `'ELEMENT TYPE'}` | {'label': 'APT ADL', 'value': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |

## ATCSCC-GOLD-034 / 2026-05-14:055

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=55
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. EFFECTIVE TIME: 141513-142330 SIGNATURE: 26/05/14 15:13 FAA.gov Home \| Privacy Policy \| Web Polic...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0412cb0ba7805cb6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:13:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPOR... |
| `cand-07777c06e2cad01f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T23:30:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPOR... |
| `cand-0ab4b69b693a6577` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T15:13:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 15:13 |
| `cand-13cca3d00d0f14aa` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 55 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-24d9e06c586ce773` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T23:30:00 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141513-142330 |
| `cand-2cb32915c866a2c5` | `S1_llm_only` | `canonical_fact` | `has_time_range` | 14/1513 - 14/2300 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/1513 - 14/2300 |
| `cand-3c9aca16c077e5a7` | `S1_llm_only` | `canonical_fact` | `should_ensure_in_flight_plan_remarks` | DVRSN | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-4a975efaa5d7a3fc` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIR... | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPOR... |
| `cand-4b9053488e41d2ea` | `S1_llm_only` | `canonical_fact` | `activated_diversion_recovery_tool_for` | SAN Diego Airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. |
| `cand-4fc73c89477c6a93` | `S1_llm_only` | `canonical_fact` | `must_include_in_flight_plan_remarks` | DVRSN | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-50030bd537fef7d8` | `S1_llm_only` | `canonical_fact` | `are_not_automatically_exempt_when` | ground delay program or ground stop in effect for destination airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-66d9e5009e57da86` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED... | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF D... |
| `cand-7d3891987879ba3f` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 55 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-8d5b823bfaedb4eb` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:13:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141513-142330 |
| `cand-9cbf640e2bce2f27` | `S1_llm_only` | `canonical_fact` | `is_constrained_facility_for_event` | SAN Airport diversion recovery | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZLA |
| `cand-ad2787f599efece8` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-14T15:13:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPOR... |
| `cand-ae702a5847260507` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T23:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141513-142330 |
| `cand-b87e162627fa7f61` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T15:13:00 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/14 15:13 |
| `cand-c1e755a2762b5407` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:13:00 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141513-142330 |
| `cand-c9a767a61f64d088` | `S1_llm_only` | `canonical_fact` | `will_still_receive` | EDCT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-ddc88cc74bbcd8be` | `S1_llm_only` | `canonical_fact` | `will_close_at` | end of the event time specified in this advisory | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-df68fa755b8806fd` | `S1_llm_only` | `canonical_fact` | `will_close_for` | SAN Airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-e367623cd654a911` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 55 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPOR... |

## ATCSCC-GOLD-035 / 2026-05-20:084

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=84
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 34

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: EWR ELEMENT TYPE: APT ADL TIME: 1644Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2000Z - 21/0359Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 20/2000Z - 21/0359Z ANTICIPATED PROGRAM RATE: 32/28/20/20/26/32/45/45 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL+CZY_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB DELAY ASSIGNMENT TABLE APPLIES TO: ZNY ANTICIPATED MAXIMUM DELAY: 150 ANTICIPATED AVERAGE DELAY: 69 IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFEREN...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b400c3699fdfaed` | `S1_llm_only` | `canonical_fact` | `has delay assignment mode` | UDP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-1baf0af3dfc19d0f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-1cd01a6e7944a7d8` | `S1_llm_only` | `canonical_fact` | `user updates must be received by` | 20/1705Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 20/1705Z |
| `cand-267a1ca330cfdcd4` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-275b86d21ad98f62` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z USER UPDATES MUST BE RECEIVED BY: 20/1705Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z USER UPDATES MUST BE RECEIVED BY: 20/1705Z |
| `cand-45334df15459a30b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T16:48:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201648-201759 |
| `cand-45587529679bdeeb` | `S1_llm_only` | `canonical_fact` | `has anticipated cumulative program period` | 20/2000Z - 21/0359Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 20/2000Z - 21/0359Z |
| `cand-45b59824489cb07a` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-5c84128707f7567c` | `S1_llm_only` | `canonical_fact` | `has anticipated average delay` | 69 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 69 |
| `cand-5e7c6e3ac6cb6e56` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-6c46ab863e55c5de` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T16:49:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 16:49 |
| `cand-6e9ab84aeb555a9e` | `S1_llm_only` | `canonical_fact` | `has anticipated program rates` | 32/28/20/20/26/32/45/45 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 32/28/20/20/26/32/45/45 |
| `cand-7719d113d9f66895` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | EWR | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-7ba9bb2f54c5aebb` | `S1_llm_only` | `canonical_fact` | `includes Canadian departure airports` | CYHZ CYOW CYUL CYYZ CYTZ CYQB | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-86ffcbf41fd1ac19` | `S1_llm_only` | `canonical_fact` | `includes flight scope` | ALL CONTIGUOUS US DEP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-88af5de7f35a2735` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:EWR | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: EWR |
| `cand-8b64cb4ff8529c3d` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 84 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-8bfffb1ec642e7ac` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z USER UPDATES MUST BE RECEIVED BY: 20/1705Z |
| `cand-94754238f59fb3b2` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | EWR | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: EWR ELEMENT TYPE: APT ADL TIME: 1644Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2000Z - 21/0359Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 20/2000Z - 21/0359Z ANTICIPATED PROGRAM RATE: 32/28/20/2... |
| `cand-974cfe0f48cec28f` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T17:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201648-201759 |
| `cand-97d0bffb28307815` | `S1_llm_only` | `canonical_fact` | `has effective time` | 201648-201759 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201648-201759 |
| `cand-addf4753c98d0b01` | `S1_llm_only` | `canonical_fact` | `has departure scope` | (ALL+CZY_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL+CZY_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-ae8a750d387f811d` | `S1_llm_only` | `canonical_fact` | `has impacting condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b7529a2940aac504` | `S1_llm_only` | `canonical_fact` | `has comment` | TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z |
| `cand-c333f686e21ebd2e` | `S1_llm_only` | `canonical_fact` | `has estimated arrival window` | 20/2000Z - 21/0359Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 20/2000Z - 21/0359Z |
| `cand-cdd53b4b93a58c26` | `S1_llm_only` | `canonical_fact` | `is advisory for control center element` | EWR | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: EWR |
| `cand-d02e2d132baf5318` | `S1_llm_only` | `canonical_fact` | `delay assignment table applies to` | ZNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZNY |
| `cand-d937060adfe397fd` | `S1_llm_only` | `canonical_fact` | `has signature timestamp` | 26/05/20 16:49 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 16:49 |
| `cand-dcfa2fa3cd201e49` | `S1_llm_only` | `canonical_fact` | `has control element type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: EWR ELEMENT TYPE: APT ADL |
| `cand-e6182620b9a11556` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-20T16:49:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-e677d69c3dc49e1a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-f4d0017f1d152612` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T03:59:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-f4f70a71b0f7f9ab` | `S1_llm_only` | `canonical_fact` | `has anticipated maximum delay` | 150 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 150 |
| `cand-fac588ae80dcc96a` | `S1_llm_only` | `canonical_fact` | `has advisory type` | CDM Proposed Ground Delay Program | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |

## ATCSCC-GOLD-036 / 2026-05-17:022

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=22
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 41

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 022 SFO/ZOA 05/17/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1245Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 17/1515Z - 17/2259Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 17/1515Z - 17/2259Z ANTICIPATED PROGRAM RATE: 36/36/36/32/36/36/36/36 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC DELAY ASSIGNMENT TABLE APPLIES TO: ZOA ANTICIPATED MAXIMUM DELAY: 91 ANTICIPATED AVERAGE DELAY: 43 IMPACTING CONDITION: OTHER / OTHER COMMENTS: CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z EFFECTIVE TIME: 171247-...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00f9f300d92ebcc9` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-0d1e5e444197b93a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-208ae6b0e85e9fbb` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | USER UPDATES MUST BE RECEIVED BY: 17/1300Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 17/1300Z |
| `cand-25793d10a7d66d6d` | `S1_llm_only` | `canonical_fact` | `'names_impacting_condition'}` | {'label': 'OTHER / OTHER', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-2d4a7d1a1c4e1a06` | `S1_llm_only` | `canonical_fact` | `'includes_canadian_departure_airports'}` | {'label': 'CYEG CYVR CYYC', 'type': 'airport_list'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-45beb4ebc65397e2` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T22:59:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ESTIMATED FOR: 17/1515Z - 17/2259Z |
| `cand-477b52a8e270f9df` | `S1_llm_only` | `canonical_fact` | `'includes_flights_scope'}` | {'label': 'ALL CONTIGUOUS US DEP DEP', 'type': 'flight_scope'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-47a6fc2fd71b5622` | `S1_llm_only` | `canonical_fact` | `'lists_delay_scope_regions'}` | {'label': 'ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP', 'type': 'scope_region_list'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-489f3eedc63d8664` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-17T12:45:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ADL TIME: 1245Z |
| `cand-4ea10ed06d19e788` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: CONFERENCE 13Z |
| `cand-518870fbb8aee157` | `S1_llm_only` | `canonical_fact` | `'states_anticipated_maximum_delay'}` | {'label': '91', 'type': 'delay_minutes'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 91 |
| `cand-5d1acca66f1a1500` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-17T12:48:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-5dbc3ef81c749abc` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | OTHER / OTHER | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-5e538c50c26b9d98` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | CONFERENCE 13Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: CONFERENCE 13Z |
| `cand-5f2ad9486c9118fc` | `S1_llm_only` | `canonical_fact` | `'states_anticipated_cumulative_program_period'}` | {'label': '17/1515Z - 17/2259Z', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 17/1515Z - 17/2259Z |
| `cand-6376dbd22adc3cb7` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T12:47:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171247-171359 |
| `cand-638903478ed09a71` | `S1_llm_only` | `canonical_fact` | `'applies_delay_assignment_table_to'}` | {'label': 'ZOA', 'type': 'air_traffic_control_area'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZOA |
| `cand-669049d7bf77b72c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T15:15:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ESTIMATED FOR: 17/1515Z - 17/2259Z |
| `cand-68af37afbe556e45` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | SFO | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-6e3a6856a8c7a970` | `S1_llm_only` | `canonical_fact` | `'identifies_control_element'}` | {'label': 'SFO element', 'type': 'airport_control_element'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-7cb2a32302319ff0` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T13:59:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-8492cb65875b12c8` | `S1_llm_only` | `canonical_fact` | `'states_anticipated_average_delay'}` | {'label': '43', 'type': 'delay_minutes'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 43 |
| `cand-8bf97b4a9428208c` | `S1_llm_only` | `canonical_fact` | `'describes_control_element_type'}` | {'label': 'APT ADL', 'type': 'control_element_type'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-920b69d2ec233f21` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z |
| `cand-9a6952aa4f5bdb18` | `S1_llm_only` | `canonical_fact` | `'is_signed_at'}` | {'label': '26/05/17 12:48', 'type': 'signature_timestamp'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/17 12:48 |
| `cand-a1fab21e15f6b820` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | other | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-a7664c815340d9eb` | `S1_llm_only` | `canonical_fact` | `'assigns_delay_mode'}` | {'label': 'UDP', 'type': 'delay_assignment_mode'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-adcff184ae82bd23` | `S1_llm_only` | `canonical_fact` | `'estimates_affected_arrival_window'}` | {'label': '17/1515Z - 17/2259Z', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 17/1515Z - 17/2259Z |
| `cand-afc705e9254df2cf` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T13:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171247-171359 |
| `cand-b26a1a8acb1b31a9` | `S1_llm_only` | `canonical_fact` | `'mentions_other_comments'}` | {'label': 'CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z', 'type': 'comment'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OTHER COMMENTS: CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z |
| `cand-bd088f1a9e0fd0fa` | `S1_llm_only` | `canonical_fact` | `'states_anticipated_program_rate'}` | {'label': '36/36/36/32/36/36/36/36', 'type': 'program_rate_sequence'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 36/36/36/32/36/36/36/36 |
| `cand-c4ffc556e57dd84f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T12:47:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-d1d4014807bff832` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 22 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 022 SFO/ZOA 05/17/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-d85b41703a64479e` | `S1_llm_only` | `canonical_fact` | `'has_effective_time_range'}` | {'label': '171247-171359', 'type': 'effective_time_range'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171247-171359 |
| `cand-dc5e46ccb5ea1748` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-e30d2587332eb5aa` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 22 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 022 SFO/ZOA 05/17/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-e430a3dd2b74da88` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT |
| `cand-ee2e7b272ca4cea0` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 22 | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-f5d407c56b00592a` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T12:48:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 12:48 |
| `cand-f903c237735aecb4` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `departureScope` | {"properties": {"atm:includesAirport": [{"label": "CYEG", "type": "nas:Airport"}, {"label": "CYVR", "type": "nas:Airport"}, {"label": "CYYC", "type": "nas:Ai... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-fb1d6f325e92843c` | `S1_llm_only` | `canonical_fact` | `'sets_ad_time'}` | {'label': '1245Z', 'type': 'zulu_time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1245Z |

## ATCSCC-GOLD-037 / 2026-05-14:040

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=40
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 45

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD: 14/1500Z - 14/2259Z PROGRAM RATE: 36/36/36/32/36/36/36/36 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1625 CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC DELAY ASSIGNMENT TABLE APPLIES TO: ZOA MAXIMUM DELAY: 108 AVERAGE DELAY: 63 IMPACTING CONDITION: OTHER / OTHER COMMENTS: ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION EFFECTIVE TIME: 141238-142359 SIGNATURE: 26/05/14 12:39 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-026e85fe896f6f50` | `S1_llm_only` | `canonical_fact` | `'effective_time_window'}` | {'label': '141238-142359'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141238-142359 |
| `cand-1129c5821327f4fe` | `S2_llm_schema_slice` | `canonical_fact` | `departureScope` | {"evidence_text": "DEP SCOPE: 1625 CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC", "type": "atm:AirportSpec"} | `{"repaired_accepted": 1}` | `{}` | DEP SCOPE: 1625 CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-12a06d4ee845ed34` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 40 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM |
| `cand-1c54b840637345a3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:00:00Z | `{"repaired_accepted": 1}` | `{}` | CUMULATIVE PROGRAM PERIOD: 14/1500Z - 14/2259Z |
| `cand-2084d2fd8209b6a6` | `S1_llm_only` | `canonical_fact` | `'estimated_for_time_window'}` | {'label': '14/1500Z - 14/2259Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z |
| `cand-20d8d0a51b8a75c3` | `S1_llm_only` | `canonical_fact` | `'flight_inclusion_scope'}` | {'label': 'ALL CONTIGUOUS US DEP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-260e320c98879de3` | `S1_llm_only` | `canonical_fact` | `'cumulative_program_period'}` | {'label': '14/1500Z - 14/2259Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 14/1500Z - 14/2259Z |
| `cand-2a308f2367a74b95` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `departureScope` | {"atm:includesAirport": [{"evidence_text": "CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC", "value": "nas:Airport:CYEG"}, {"evidence_text": "CANADIAN DEP ARPTS... | `{"repaired_accepted": 1}` | `{}` | DEP SCOPE: 1625 CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-308fe459ce415666` | `S2_llm_schema_slice` | `canonical_fact` | `flightInclusionSpec` | {"evidence_text": "FLT INCL: ALL CONTIGUOUS US DEP", "type": "urn:absolute:icarus#FlightSpec"} | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-3c366d77fc742a3f` | `S1_llm_only` | `canonical_fact` | `'delay_assignment_table_applies_to'}` | {'label': 'ZOA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZOA |
| `cand-41a5bb417499d353` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | nas:Airport:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z |
| `cand-45ec501abceaaf8c` | `S1_llm_only` | `canonical_fact` | `'reason_for_program'}` | {'label': 'procedural compliance and runway construction'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION |
| `cand-4759781385191f47` | `S1_llm_only` | `canonical_fact` | `'program_rate_sequence'}` | {'label': '36/36/36/32/36/36/36/36'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 36/36/36/32/36/36/36/36 |
| `cand-4a2130d6b56c5fa5` | `S1_llm_only` | `canonical_fact` | `'scope_applies_to'}` | {'label': '1625 Canadian departure airports included'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: 1625 CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-599bdfbc8f9693ee` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 40 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD... |
| `cand-5c8f7ce1933cef9b` | `S1_llm_only` | `canonical_fact` | `'average_delay_minutes'}` | {'label': '63'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 63 |
| `cand-6142f2e790e85648` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T23:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141238-142359 |
| `cand-6e3fcc7f17621ef0` | `S1_llm_only` | `canonical_fact` | `'announces_ground_delay_program'}` | {'label': 'CDM ground delay program'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM |
| `cand-7397accc7dbdb6a4` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:00:00Z | `{"repaired_accepted": 1}` | `{}` | ESTIMATED FOR: 14/1500Z - 14/2259Z |
| `cand-77c2910e9a025efe` | `S1_llm_only` | `canonical_fact` | `'time_plus_value'}` | {'label': '45'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME PLUS 45 |
| `cand-7c6d9e2114e08f13` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-81fc265072606fc1` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T22:59:00Z | `{"repaired_accepted": 1}` | `{}` | CUMULATIVE PROGRAM PERIOD: 14/1500Z - 14/2259Z |
| `cand-875748a7860f2a8a` | `S1_llm_only` | `canonical_fact` | `'departure_runway_configuration'}` | {'label': '28LR'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP: 28LR |
| `cand-87b3e4997f545cdb` | `S1_llm_only` | `canonical_fact` | `'impacting_condition'}` | {'label': 'OTHER / OTHER'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-8949c076802a7218` | `S1_llm_only` | `canonical_fact` | `'arrival_runway_configuration'}` | {'label': '28L/R'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARR: 28L/R |
| `cand-9021468e742a8a8f` | `S1_llm_only` | `canonical_fact` | `'low_historical_probability_pop_up'}` | {'label': 'true'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | LOW HIST. POP UP. |
| `cand-913d950a47d3a940` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {"evidence_text": "CTL ELEMENT: SFO ELEMENT TYPE: APT", "type": "nas:Airport"} | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT |
| `cand-99d9aab6c7ff8a32` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:00:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD... |
| `cand-a1466f133b6b74b9` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T22:59:00Z | `{"repaired_accepted": 1}` | `{}` | ESTIMATED FOR: 14/1500Z - 14/2259Z |
| `cand-a44274a9a68fea46` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-a6077a867d946c5b` | `S1_llm_only` | `canonical_fact` | `'controlled_by'}` | {'label': 'SFO element'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-a78afd881e8adbe0` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T12:39:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 12:39 |
| `cand-a7d744b27455c20a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-14T12:33:00Z | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z |
| `cand-a97b191473b41f9d` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T12:33:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD... |
| `cand-b4382e40a0962518` | `S1_llm_only` | `canonical_fact` | `'delay_assignment_mode'}` | {'label': 'UDP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-c4d64284a82e9a0d` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD... |
| `cand-d0171c531456d412` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T22:59:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD... |
| `cand-d2ff88dd7c5a1bf9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T12:38:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141238-142359 |
| `cand-d61205c9cb471f29` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD... |
| `cand-eafa4abddfe34464` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION |
| `cand-eb85cec9b73516c4` | `S1_llm_only` | `canonical_fact` | `'element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL |
| `cand-f1253bbadd3f4cc9` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION |
| `cand-f47af82a9a61b007` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION |
| `cand-fadfb5041fe26f6f` | `S1_llm_only` | `canonical_fact` | `'maximum_delay_minutes'}` | {'label': '108'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 108 |
| `cand-fc2117c984a9dfb9` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | OTHER / OTHER | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |

## ATCSCC-GOLD-038 / 2026-05-20:115

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=115
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 31

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD: 20/1700Z - 21/0359Z PROGRAM RATE: 18/18/22/24/24/24/24 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1425 CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB DELAY ASSIGNMENT TABLE APPLIES TO: ZNY MAXIMUM DELAY: 272 AVERAGE DELAY: 97 IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. EFFECTIVE TIME: 201857-210459 SIGNATURE: 26/05/20 18:59 FAA.gov Home \| Privacy Policy \| Web Policies &...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02181c8d7e8be602` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'delay_assignment_mode', 'text': 'UDP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-036242b9822104d0` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'rate_sequence', 'text': '18/18/22/24/24/24/24'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 18/18/22/24/24/24/24 |
| `cand-06191c699e48f767` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1f0d5767284eb7a0` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 115 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-21403bfb60101e69` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'airport_and_center_area', 'text': 'LGA/ZNY'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM |
| `cand-252adb2e56b05cfa` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'airport', 'text': 'LGA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LGA |
| `cand-3a0f65cd5bdd7080` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'comment', 'text': 'ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS.'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. |
| `cand-4ab1468cb55b37c9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T18:57:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201857-210459 |
| `cand-4c0ab9883a4f144a` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'time_window', 'text': '20/1700Z - 21/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 20/1700Z - 21/0359Z |
| `cand-4f776ce78dcd2597` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LGA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: LGA |
| `cand-5e3de266ac4eeb23` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T04:59:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-73bfdf180d1d7434` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'airport_list', 'text': 'CYHZ CYOW CYUL CYYZ CYTZ CYQB'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-7f9b32b34135a69f` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-88ad5183c21e9e6f` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-8b2a266434ef0fc7` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | LGA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | CTL ELEMENT: LGA ELEMENT TYPE: APT |
| `cand-8f21f844454619c3` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'effective_time_range', 'text': '201857-210459'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201857-210459 |
| `cand-93ed92f6ae20e9b7` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'center', 'text': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZNY |
| `cand-9dd1708be2f83131` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a030b7cd054fa548` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b3b7ec457847e36c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T18:57:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-b608bd2acd748b65` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T18:59:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-b8fa90565d768e1d` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T04:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201857-210459 |
| `cand-ba173bebea76d411` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | LGA | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-d0fa4836bf3de8a9` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'weather_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d736d29deb4e3aad` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'time_window', 'text': '20/2100Z - 21/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z |
| `cand-dda8db8ffd009884` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'flight_scope', 'text': 'ALL CONTIGUOUS US DEP DEP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-e04e0b773a133b34` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'delay_minutes', 'text': '97'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 97 |
| `cand-e6328880c270f89f` | `S1_llm_only` | `canonical_fact` | `unmapped_payload` | {'class_label': 'delay_minutes', 'text': '272'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 272 |
| `cand-ec55c83854e4d643` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. |
| `cand-ed7890f810f14261` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 115 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM |
| `cand-f14fa0474f1f1232` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T18:59:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 18:59 |

## ATCSCC-GOLD-039 / 2026-05-18:075

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=75
- Candidate class: `GroundStopTMI`
- Current status: `reviewed`
- Candidate clusters: 48

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI RAW TEXT: EVENT TIME: 18/1630 - 18/2230 CONSTRAINED FACILITIES: ZMA THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT. CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS AND ANTICIPATE ALTERNATE ROUTES. ZMA SWAP STATEMENT: SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR ZMA AIRSPACE AND SOUTH FLORIDA TERMINAL AREAS AFTER 1630Z WEATHER CONSTRAINTS: THUNDERSTORMS ARE EXPECTED TO IMPACT SOUTH FLORIDA DEPARTURE AND ARRIVAL ROUTES AND A MAJORITY OF ZMA AIRSPACE. PLANNED ALTERNATE DEPARTURE ROUTES: ALL GATES ARE ANTICIPATED TO BE IMPACTED DUE TO THE NATURE OF...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05d2de33894d5470` | `S1_llm_only` | `canonical_fact` | `are_reserved_for` | ATC determination | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THESE ROUTES ARE RESERVED FOR ATC DETERMINATION. |
| `cand-072d77ffba77d9fd` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZMA | `{"repaired_accepted": 1}` | `{}` | CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITHIN THE SOUTH FLORIDA TERMINAL AREA. |
| `cand-12ae194f6226f3a1` | `S1_llm_only` | `canonical_fact` | `are_expected_for` | ZMA airspace and South Florida terminal areas after 1630Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR ZMA AIRSPACE AND SOUTH FLORIDA TERMINAL AREAS AFTER 1630Z |
| `cand-16ca9d4c07a93465` | `S1_llm_only` | `canonical_fact` | `cause` | additional departure delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO LIMITED ESCAPE ROUTES. |
| `cand-177065696b75f18f` | `S1_llm_only` | `canonical_fact` | `should_anticipate` | alternate routes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATE ALTERNATE ROUTES. |
| `cand-1e7c8b62435c54be` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | DO NOT FILE CDR'S THAT END IN 2 OR 3. THESE ROUTES ARE RESERVED FOR ATC DETERMINATION. |
| `cand-1f509aaaa2fc5af6` | `S1_llm_only` | `canonical_fact` | `require` | appropriate over flight permits | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INTERNATIONAL CDR'S REQUIRE APPROPRIATE OVER FLIGHT PERMITS. |
| `cand-20b0adf3c61eb580` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | PLAYBOOK | `{"repaired_accepted": 1}` | `{}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-20d1051116d9db66` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-2e6d693cfdf96c6f` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZMA | `{"repaired_accepted": 1}` | `{}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-351cfe97a3e073d4` | `S1_llm_only` | `canonical_fact` | `are_causing` | coded departure routes and/or swaps out of an alternate gate | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO THE NATURE OF THE THUNDERSTORMS CAUSING CODED DEPARTURE ROUTES AND/OR SWAPS OUT OF AN ALTERNATE GATE. |
| `cand-36910de6424e02cd` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-37a73786c98ace62` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT. CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS AND ANTICIPATE ALTERNATE ROUTES. |
| `cand-3f44b228bdda7e58` | `S1_llm_only` | `canonical_fact` | `has_constrained_facility` | ZMA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA |
| `cand-43303b517284c565` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-55da06227f12e21e` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | THUNDERSTORMS ARE EXPECTED TO IMPACT SOUTH FLORIDA DEPARTURE AND ARRIVAL ROUTES AND A MAJORITY OF ZMA AIRSPACE. |
| `cand-5b466dba218667f1` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITHIN THE SOUTH FLORIDA TERMINAL AREA. |
| `cand-6bd96c1acecb5572` | `S1_llm_only` | `canonical_fact` | `can_expect` | additional departure delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHTS THAT CANNOT FLY MORE THAN 162NM OFFSHORE CAN EXPECT ADDITIONAL DEPARTURE DELAYS |
| `cand-6ea2e8c2dd7017fd` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZMA | `{"repaired_accepted": 1}` | `{}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT. CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS AND ANTICIPATE ALTERNATE ROUTES. |
| `cand-71f4c248ab065ddf` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-72d6654104bb87db` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | EVENT TIME: 18/1630 - 18/2230 CONSTRAINED FACILITIES: ZMA THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROU... | `{"repaired_accepted": 1}` | `{}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-7473b16f60fe2452` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZMA | `{"repaired_accepted": 1}` | `{}` | THUNDERSTORMS ARE EXPECTED TO IMPACT SOUTH FLORIDA DEPARTURE AND ARRIVAL ROUTES AND A MAJORITY OF ZMA AIRSPACE. |
| `cand-77eedac642ebca42` | `S1_llm_only` | `canonical_fact` | `are_anticipated_to_be_impacted` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ALL GATES ARE ANTICIPATED TO BE IMPACTED |
| `cand-785000144370f738` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-79de4537175a74df` | `S1_llm_only` | `canonical_fact` | `can_expect` | possible playbooks, tactical route adjustments, holding on inbound flights, and ZMA ground stops | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS |
| `cand-7a3c05366d28344d` | `S1_llm_only` | `canonical_fact` | `are_expected_to_impact` | South Florida departure and arrival routes and a majority of ZMA airspace | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THUNDERSTORMS ARE EXPECTED TO IMPACT SOUTH FLORIDA DEPARTURE AND ARRIVAL ROUTES AND A MAJORITY OF ZMA AIRSPACE. |
| `cand-817dbcaafb35c7fa` | `S1_llm_only` | `canonical_fact` | `are_encouraged_to_comply_with` | all ATCSCC route advisories | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. |
| `cand-84d5e195be32a8ff` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT. CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS AND ANTICIPATE ALTERNATE ROUTES. |
| `cand-86261872ca2dab3e` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | PLAYBOOK | `{"repaired_accepted": 1}` | `{}` | ZMA SWAP_FYI |
| `cand-8ba680942cf94a55` | `S1_llm_only` | `canonical_fact` | `should_not_be_filed` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DO NOT FILE CDR'S THAT END IN 2 OR 3. |
| `cand-99d0804c12274b13` | `S1_llm_only` | `canonical_fact` | `has_event_time_window` | 18/1630 - 18/2230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1630 - 18/2230 |
| `cand-9c44b99f7b270a9d` | `S1_llm_only` | `canonical_fact` | `is_for_planning_purposes_only` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-ae1bc90444f07d15` | `S1_llm_only` | `canonical_fact` | `affect` | airspace surrounding and within the South Florida terminal area | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITHIN THE SOUTH FLORIDA TERMINAL AREA. |
| `cand-b235a42f83d553ec` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITHIN THE SOUTH FLORIDA TERMINAL AREA. |
| `cand-b53c182538f9183c` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-b8f67136015825b6` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 75 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-be848bb407dfc962` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | CDR | `{"repaired_accepted": 1}` | `{}` | DO NOT FILE CDR'S THAT END IN 2 OR 3. THESE ROUTES ARE RESERVED FOR ATC DETERMINATION. |
| `cand-c7d4ada26e25becc` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | EVENT TIME: 18/1630 - 18/2230 CONSTRAINED FACILITIES: ZMA THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROU... | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-cf63838736f985c2` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-d3194ffdf9c02f04` | `S1_llm_only` | `canonical_fact` | `should_fuel_accordingly_for` | possible departure/arrival gate changes, playbooks, tactical reroutes, holding and other traffic management initiatives | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE FUEL ACCORDINGLY FOR POSSIBLE DEPARTURE/ ARRIVAL GATE CHANGES, PLAYBOOKS, TACTICAL REROUTES, HOLDING AND OTHER TRAFFIC MANAGEMENT INITIATIVES |
| `cand-d8835b30719ce67b` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZMA | `{"repaired_accepted": 1}` | `{}` | DO NOT FILE CDR'S THAT END IN 2 OR 3. THESE ROUTES ARE RESERVED FOR ATC DETERMINATION. |
| `cand-db3f7b1f38b1ddff` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ZMA SWAP_FYI |
| `cand-ddf7713bc554a406` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZMA | `{"repaired_accepted": 1}` | `{}` | ZMA SWAP_FYI |
| `cand-e862b84c00dbd293` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT. CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS AND ANTICIPATE ALTERNATE ROUTES. |
| `cand-f14f24a02921b2e4` | `S1_llm_only` | `canonical_fact` | `are_encouraged_to_file` | normal routings | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS |
| `cand-f517a82139871dcf` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteType` | PLAYBOOK | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-f68376e7063443f3` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | DO NOT FILE CDR'S THAT END IN 2 OR 3. THESE ROUTES ARE RESERVED FOR ATC DETERMINATION. |
| `cand-fbfc9d99426dd503` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ZMA SWAP_FYI |

## ATCSCC-GOLD-040 / 2026-05-20:197

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=197
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 15

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION MESSAGE: ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 202359-210200 SIGNATURE: 26/05/20 23:59 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0151d7b5e8976bd1` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {'name': 'ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. |
| `cand-0916c4248b064e90` | `S1_llm_only` | `canonical_fact` | `has_remark` | associated restrictions | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-12fca6001e102b93` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 197 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-218acd50f943af4d` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T23:59:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 23:59 |
| `cand-26002cb331bb77dd` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202359-210200 |
| `cand-29df9dfd7d6d3015` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-2d953801a51fee79` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-36a00cee0e02cedd` | `S1_llm_only` | `canonical_fact` | `advisory_message_type` | reroute cancellation | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-544d7203ee032079` | `S1_llm_only` | `canonical_fact` | `cancellation_status` | cancelled | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. |
| `cand-5f7265f39c9c1835` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | OTHER | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-76cf775e02890168` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | INFORMATIONAL | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-8ddf61aa108b2d0b` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T23:59:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 23:59 |
| `cand-95df21765497c626` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 202359-210200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202359-210200 |
| `cand-a04d6f47a774c8e7` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 197 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-ffda238e74aa07e9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T23:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202359-210200 |
