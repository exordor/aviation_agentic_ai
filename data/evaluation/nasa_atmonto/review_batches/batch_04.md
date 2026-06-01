# NASA ATMONTO Gold Review batch_04

- Samples: `ATCSCC-GOLD-031` to `ATCSCC-GOLD-040`
- Records: 10
- Candidate clusters: 249

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-031 / 2026-05-19:011

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=11
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0409Z GROUND STOP PERIOD: 19/0400Z - 19/0515Z CUMULATIVE PROGRAM PERIOD: 18/1515Z - 19/0659Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 142 / 63 / 16 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 772 / 228 / 86 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: OTHER / OTHER COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. EFFECTIVE TIME: 190409-190615 SIGNATURE: 26/05/19 04:10 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-07848f5ff9a2d6fb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_ground_stop_period'}` | {'class': 'time_interval', 'text': '19/0400Z - 19/0515Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 19/0400Z - 19/0515Z |
| `cand-0f51757c66398192` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is_impacted_by_condition'}` | {'class': 'impacting_condition', 'text': 'OTHER / OTHER'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-0f9a55ba0111b54b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces'}` | {'class': 'traffic_management_program', 'text': 'GROUND STOP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP |
| `cand-31923bff16b218d0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'facility_group', 'text': 'ZLA ZLC ZOA ZSE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE |
| `cand-367caffb196d2542` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T04:10:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 04:10 |
| `cand-3a3e3bc5b17f8827` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_probability_of_extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-40973cf3ec88624b` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | OTHER / OTHER | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-45a82f1214eea374` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-47cd5986d8c6c657` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T04:09:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190409-190615 |
| `cand-49ee17f407651abe` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_cumulative_program_period'}` | {'class': 'time_interval', 'text': '18/1515Z - 19/0659Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 18/1515Z - 19/0659Z |
| `cand-4d8fc4b4f54ac1dc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_advisory_time'}` | {'class': 'zulu_time', 'text': '0409Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 0409Z |
| `cand-51912a56a396fb87` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: SFO", "value": "SFO"}], "atm:effectiveEndTime": [{"evidence_text": "GROUND STOP PERIOD: 19/0400... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0409Z GROUND STOP PERIOD: 19/0400Z - 19/0515Z CUMULATIVE PROGRAM PERIOD: 18/1515Z - 19/0659Z DEP FACILITIES INC... |
| `cand-62bd718ed1c6d853` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_effective_time'}` | {'class': 'effective_time_interval', 'text': '190409-190615'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190409-190615 |
| `cand-773cb82efc15d0fd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'new_delays_reported_as'}` | {'class': 'delay_statistics', 'text': '772 / 228 / 86'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 772 / 228 / 86 |
| `cand-92667605cfd166b5` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-964d9c1174043e81` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-a474d73b930e1f06` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'previous_delays_reported_as'}` | {'class': 'delay_statistics', 'text': '142 / 63 / 16'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 142 / 63 / 16 |
| `cand-bc3ea3660469da1b` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T06:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190409-190615 |
| `cand-bca3d6ce5949a1bd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_control_element_type'}` | {'class': 'control_element_type', 'text': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-ce9609e9e53282a3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'applies_to_control_element'}` | {'class': 'facility', 'text': 'SFO'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-e649736ac9016213` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-eb5072224f11009a` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 11 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP |
| `cand-f01ac060bee4e842` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_comment_explaining_cause'}` | {'class': 'comment', 'text': 'DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION.'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |

## ATCSCC-GOLD-032 / 2026-05-20:131

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=131
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
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
| `cand-09bf3062d3a71274` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 131 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-0a86825a7024310b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-0cecac67571972d3` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1518fddef0e615c6` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD |
| `cand-214dacfae4fd3177` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | IAD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD |
| `cand-267adb4d3c1a4649` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1957Z GROUND STOP PERIOD: 20/1947Z - 20/2130Z", "value": "IAD"}... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-2df2ef06b44d9808` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_delays` | 1387 / 68 / 30 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1387 / 68 / 30 |
| `cand-39a1abda6cd9af66` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T22:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202001-202230 |
| `cand-4047a17a33e7ed4d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_delays` | 4276 / 171 / 93 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 4276 / 171 / 93 |
| `cand-552131283e75be05` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-559051b34033e226` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 131 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-77d8b20a7c598371` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-80fd158a2848f1bc` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-20T22:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-92b60acb529eccc9` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-20T20:02:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 20:02 |
| `cand-9703640397028644` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | GROUND STOP EXTENSION. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | COMMENTS: GROUND STOP EXTENSION. |
| `cand-9ae972c0cb147f8a` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | GROUND STOP EXTENSION. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: GROUND STOP EXTENSION. |
| `cand-9cd88ea728114406` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-ae213b131914b96d` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-aefa9ea47d53bcda` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:01:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202001-202230 |
| `cand-c2342d8f5568b8d1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 202001-202230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-d1dc7bb4b0585dc2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_comment` | GROUND STOP EXTENSION. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: GROUND STOP EXTENSION. |
| `cand-d43fa13f12ff89d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_adl_time` | 1957Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADT TIME: 1957Z |
| `cand-d4793d926bdbcb0f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-20T20:02:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-dc45f58b42f0dd76` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-dfa11431d6cde419` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e79119e757730bcf` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e9a9d34342e3c8e0` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T20:02:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 20:02 |
| `cand-f130d41a74fbd099` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facilities` | ZTL ZDC ZNY ZJX ZOB ZBW ZID | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-f40dc8b59d8e018a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element` | IAD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD |
| `cand-f97a5d04f0ee5cd3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `describes_ground_stop_period` | 20/1947Z - 20/2130Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/1947Z - 20/2130Z |

## ATCSCC-GOLD-033 / 2026-05-18:025

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=25
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
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
| `cand-1287b7646d856ce9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T07:50:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180750-181954 |
| `cand-273ac996acea4084` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'GDP CNX PERIOD'}` | {'label': '18/0750Z - 18/1854Z', 'value': '18/0750Z - 18/1854Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GDP CNX PERIOD: 18/0750Z - 18/1854Z |
| `cand-47cd9aefd04128f8` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:LAS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS ELEMENT TYPE: APT |
| `cand-5795d222daef36cd` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T19:54:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-5bccad478205a0ab` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 25 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-6a57e3253ef88e91` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `controlledNASelement` | {"atm:controlledNASelement": {"label": "LAS", "type": "nas:Airport"}} | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-851b995f0e0ad673` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T07:50:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 07:50 |
| `cand-8ff4615cf5c01a54` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T19:54:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180750-181954 |
| `cand-934208a4f24bd1ec` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: LAS |
| `cand-9a24e391a51a3208` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'ELEMENT TYPE'}` | {'label': 'APT ADL', 'value': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-ad06f8f96ddd7b49` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'EFFECTIVE TIME'}` | {'label': '180750-181954', 'value': '180750-181954'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-aeb734d2bebc0545` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | DISREGARD EDCTS FOR DEST LAS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | COMMENTS: EFFECTIVE TIME: 180750-181954 |
| `cand-c1885f25468ab39e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'GDP CNX'}` | {'label': 'ground delay program cancellation', 'value': 'GDP CNX'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-c74e9d69cc37f749` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'CTL ELEMENT'}` | {'label': 'LAS', 'value': 'LAS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS |
| `cand-cb23ed260a9da540` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'DISREGARD'}` | {'label': 'EDCTS for destination LAS', 'value': 'EDCTS FOR DEST LAS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISREGARD EDCTS FOR DEST LAS |
| `cand-db8e8ae01946a444` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'ADL TIME'}` | {'label': '0750Z', 'value': '0750Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 0750Z |
| `cand-e8114480d7ee5fef` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 25 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-f425d44c55b948ff` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-fbc2e124d9009aac` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T07:50:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |

## ATCSCC-GOLD-034 / 2026-05-14:055

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=55
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. EFFECTIVE TIME: 141513-142330 SIGNATURE: 26/05/14 15:13 FAA.gov Home \| Privacy Policy \| Web Polic...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0ab4b69b693a6577` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T15:13:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 15:13 |
| `cand-14ca435391265a45` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-14T23:30:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141513-142330 |
| `cand-23965e3d8f7e5ea3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_constrained_facility_for_event` | SAN Airport diversion recovery | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZLA |
| `cand-24d233251bfc0724` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF D... |
| `cand-27f81eb31e1b338e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `will_still_receive` | EDCT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-3ac4d11d83f59393` | `S1_llm_only` | `freeform_or_unmapped_fact` | `will_close_for` | SAN Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-3b2fcf22b678bb04` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 55 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-61037db7e6965379` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should_ensure_in_flight_plan_remarks` | DVRSN | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-72ef5791e3692955` | `S1_llm_only` | `freeform_or_unmapped_fact` | `activated_diversion_recovery_tool_for` | SAN Diego Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. |
| `cand-7d3891987879ba3f` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 55 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-844de387b9b2dda2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_time_range` | 14/1513 - 14/2300 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/1513 - 14/2300 |
| `cand-8d5b823bfaedb4eb` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:13:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141513-142330 |
| `cand-9bd441ee38e1987d` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-14T15:13:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/14 15:13 |
| `cand-ae702a5847260507` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T23:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141513-142330 |
| `cand-bb65abced3050312` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_not_automatically_exempt_when` | ground delay program or ground stop in effect for destination airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-caf3d5b9b06dd73b` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 55, "atm:effectiveEndTime": "2026-05-14T23:30:00", "atm:effectiveStartTime": "2026-05-14T15:13:00", "atm:initiativeComments": "ATCSCC... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPOR... |
| `cand-e2d0680a174df660` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-14T15:13:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141513-142330 |
| `cand-ed4ecb8972579e5b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `will_close_at` | end of the event time specified in this advisory | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-ee7d37244f032232` | `S1_llm_only` | `freeform_or_unmapped_fact` | `must_include_in_flight_plan_remarks` | DVRSN | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |

## ATCSCC-GOLD-035 / 2026-05-20:084

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=84
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: EWR ELEMENT TYPE: APT ADL TIME: 1644Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2000Z - 21/0359Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 20/2000Z - 21/0359Z ANTICIPATED PROGRAM RATE: 32/28/20/20/26/32/45/45 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL+CZY_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB DELAY ASSIGNMENT TABLE APPLIES TO: ZNY ANTICIPATED MAXIMUM DELAY: 150 ANTICIPATED AVERAGE DELAY: 69 IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFEREN...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0ff984cc6c5f1d85` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has control element type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: EWR ELEMENT TYPE: APT ADL |
| `cand-2089b36ac843cc96` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"@type": "nas:Airport", "label": "EWR"}, "atm:effectiveEndTime": "2026-05-21T03:59:00Z", "atm:effectiveStartTime": "2026-05-20T... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-267a1ca330cfdcd4` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-273ef4ff937d3447` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory type` | CDM Proposed Ground Delay Program | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-275b86d21ad98f62` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z USER UPDATES MUST BE RECEIVED BY: 20/1705Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z USER UPDATES MUST BE RECEIVED BY: 20/1705Z |
| `cand-2ea02f0e5a62ddff` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has effective time` | 201648-201759 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201648-201759 |
| `cand-45334df15459a30b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T16:48:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201648-201759 |
| `cand-45b59824489cb07a` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-540a347464f9520d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has estimated arrival window` | 20/2000Z - 21/0359Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 20/2000Z - 21/0359Z |
| `cand-5753cca9e2a9dca1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has impacting condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-61184d53bb72ae94` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is advisory for control center element` | EWR | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: EWR |
| `cand-6257b0d7c3166e79` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has anticipated maximum delay` | 150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 150 |
| `cand-669ccf20b7b239c9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has delay assignment mode` | UDP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-6c46ab863e55c5de` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T16:49:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 16:49 |
| `cand-6d35190ee889d399` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has anticipated cumulative program period` | 20/2000Z - 21/0359Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 20/2000Z - 21/0359Z |
| `cand-796ab76960c5f18f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has anticipated program rates` | 32/28/20/20/26/32/45/45 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 32/28/20/20/26/32/45/45 |
| `cand-7cb3fff626cf20aa` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: EWR ELEMENT TYPE: APT ADL TIME: 1644Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/200... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-7e29214074506fb7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has anticipated average delay` | 69 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 69 |
| `cand-88af5de7f35a2735` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:EWR | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: EWR |
| `cand-8b64cb4ff8529c3d` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 84 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-94d8092072978be9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes Canadian departure airports` | CYHZ CYOW CYUL CYYZ CYTZ CYQB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-974cfe0f48cec28f` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T17:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201648-201759 |
| `cand-9bd11eb8ff205620` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes flight scope` | ALL CONTIGUOUS US DEP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-a8d82743afdd09b9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has signature timestamp` | 26/05/20 16:49 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 16:49 |
| `cand-aa09b169ecfb8152` | `S1_llm_only` | `freeform_or_unmapped_fact` | `user updates must be received by` | 20/1705Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 20/1705Z |
| `cand-aedc8e345efa0690` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has departure scope` | (ALL+CZY_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL+CZY_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-be951a7d7d160fbd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has comment` | TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: TSTMS AND SWAP EXPECTED. LOW POPUP. TIME + 45. CONFERENCE AT 1705Z |
| `cand-e590c8619ef3086b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `delay assignment table applies to` | ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZNY |

## ATCSCC-GOLD-036 / 2026-05-17:022

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=22
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 34

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
| `cand-0687fbde904850f9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is_signed_at'}` | {'label': '26/05/17 12:48', 'type': 'signature_timestamp'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/17 12:48 |
| `cand-255de9f82470806a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-17T15:15:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ESTIMATED FOR: 17/1515Z - 17/2259Z |
| `cand-292e4fd1d2f49aec` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_canadian_departure_airports'}` | {'label': 'CYEG CYVR CYYC', 'type': 'airport_list'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-2cad818a6720203a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT |
| `cand-301182fc0387a9ce` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_effective_time_range'}` | {'label': '171247-171359', 'type': 'effective_time_range'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171247-171359 |
| `cand-3a1105c842dd047a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | CONFERENCE 13Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: CONFERENCE 13Z |
| `cand-3c1f9968fb913310` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimates_affected_arrival_window'}` | {'label': '17/1515Z - 17/2259Z', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 17/1515Z - 17/2259Z |
| `cand-49b43d1b30cebfdf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'describes_control_element_type'}` | {'label': 'APT ADL', 'type': 'control_element_type'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-5dbc3ef81c749abc` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | OTHER / OTHER | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-5dec044257ac035f` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 22, "atm:controlledNASelement": {"label": "SFO", "type": "nas:Airport"}, "atm:departureScope": {"properties": {"atm:includesAirport":... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-6376dbd22adc3cb7` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T12:47:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171247-171359 |
| `cand-6b07d90d59972e63` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_anticipated_cumulative_program_period'}` | {'label': '17/1515Z - 17/2259Z', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 17/1515Z - 17/2259Z |
| `cand-777449cdfa6dab95` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_flights_scope'}` | {'label': 'ALL CONTIGUOUS US DEP DEP', 'type': 'flight_scope'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-7be04bfc317e28ae` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_anticipated_average_delay'}` | {'label': '43', 'type': 'delay_minutes'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 43 |
| `cand-7d6c5a090b471b08` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-17T22:59:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ESTIMATED FOR: 17/1515Z - 17/2259Z |
| `cand-84bfba716b3e2bb7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'lists_delay_scope_regions'}` | {'label': 'ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP', 'type': 'scope_region_list'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-855085b7c4de8009` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'mentions_other_comments'}` | {'label': 'CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z', 'type': 'comment'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OTHER COMMENTS: CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z |
| `cand-87c0457880016b98` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_control_element'}` | {'label': 'SFO element', 'type': 'airport_control_element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-897d0c5ec8e3370d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'applies_delay_assignment_table_to'}` | {'label': 'ZOA', 'type': 'air_traffic_control_area'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZOA |
| `cand-8a176e025625240a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-17T12:45:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ADL TIME: 1245Z |
| `cand-920b69d2ec233f21` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: CONFERENCE 13Z USER UPDATES MUST BE RECEIVED BY: 17/1300Z |
| `cand-925f683d1cef648c` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | USER UPDATES MUST BE RECEIVED BY: 17/1300Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 17/1300Z |
| `cand-98e13e893ff3d372` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names_impacting_condition'}` | {'label': 'OTHER / OTHER', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-9a6bd871c46a91fb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'assigns_delay_mode'}` | {'label': 'UDP', 'type': 'delay_assignment_mode'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-9ec6124b1d16db4d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_anticipated_maximum_delay'}` | {'label': '91', 'type': 'delay_minutes'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 91 |
| `cand-afc705e9254df2cf` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T13:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171247-171359 |
| `cand-b3b18ddb85ebbe87` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_anticipated_program_rate'}` | {'label': '36/36/36/32/36/36/36/36', 'type': 'program_rate_sequence'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 36/36/36/32/36/36/36/36 |
| `cand-b4566dee3fa6f2a3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'sets_ad_time'}` | {'label': '1245Z', 'type': 'zulu_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1245Z |
| `cand-beac43aa097438d5` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 22 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 022 SFO/ZOA 05/17/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-dc5e46ccb5ea1748` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-e30d2587332eb5aa` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 22 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 022 SFO/ZOA 05/17/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-f5d407c56b00592a` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T12:48:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 12:48 |
| `cand-f95dab93e725d7f8` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | other | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: CONFERENCE 13Z |

## ATCSCC-GOLD-037 / 2026-05-14:040

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=40
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD: 14/1500Z - 14/2259Z PROGRAM RATE: 36/36/36/32/36/36/36/36 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1625 CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC DELAY ASSIGNMENT TABLE APPLIES TO: ZOA MAXIMUM DELAY: 108 AVERAGE DELAY: 63 IMPACTING CONDITION: OTHER / OTHER COMMENTS: ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION EFFECTIVE TIME: 141238-142359 SIGNATURE: 26/05/14 12:39 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01883503b278fe27` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'scope_applies_to'}` | {'label': '1625 Canadian departure airports included'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: 1625 CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-03494708666b115f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'cumulative_program_period'}` | {'label': '14/1500Z - 14/2259Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 14/1500Z - 14/2259Z |
| `cand-039f1e9cc1f07783` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'flight_inclusion_scope'}` | {'label': 'ALL CONTIGUOUS US DEP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-12a06d4ee845ed34` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 40 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM |
| `cand-12b2413bf36731af` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'maximum_delay_minutes'}` | {'label': '108'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 108 |
| `cand-150f4cf16f70a7ab` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'arrival_runway_configuration'}` | {'label': '28L/R'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARR: 28L/R |
| `cand-240b1fbddc97d409` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated_for_time_window'}` | {'label': '14/1500Z - 14/2259Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z |
| `cand-30b44a45d7a65d51` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z", "value": "nas:Airport:SFO"}], "atm:departureScope": [{"... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-34c7ab27a4a3b10d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'effective_time_window'}` | {'label': '141238-142359'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141238-142359 |
| `cand-444defe2b2ff0a55` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'delay_assignment_mode'}` | {'label': 'UDP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-6142f2e790e85648` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T23:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141238-142359 |
| `cand-6abb69447e9c0fc1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'controlled_by'}` | {'label': 'SFO element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-6d8ad3d8834f2549` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL |
| `cand-7351b5d0d015f7a4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'time_plus_value'}` | {'label': '45'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME PLUS 45 |
| `cand-7c6d9e2114e08f13` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-9c0672709f243d70` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'average_delay_minutes'}` | {'label': '63'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 63 |
| `cand-9e947417dbc4aedc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'delay_assignment_table_applies_to'}` | {'label': 'ZOA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZOA |
| `cand-9fe10c0a60245532` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'departure_runway_configuration'}` | {'label': '28LR'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP: 28LR |
| `cand-a44274a9a68fea46` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-a78afd881e8adbe0` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T12:39:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 12:39 |
| `cand-b88223b0bfcc1ad9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_ground_delay_program'}` | {'label': 'CDM ground delay program'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM |
| `cand-c07f42d0e0e15198` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reason_for_program'}` | {'label': 'procedural compliance and runway construction'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION |
| `cand-c1019777d761b82b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'impacting_condition'}` | {'label': 'OTHER / OTHER'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-d2ff88dd7c5a1bf9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T12:38:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141238-142359 |
| `cand-e1c3d6595ec2c7a7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'program_rate_sequence'}` | {'label': '36/36/36/32/36/36/36/36'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 36/36/36/32/36/36/36/36 |
| `cand-e78bd2d8b4ac36fe` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'low_historical_probability_pop_up'}` | {'label': 'true'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | LOW HIST. POP UP. |
| `cand-eafa4abddfe34464` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ARR: 28L/R DEP: 28LR TIME PLUS 45 LOW HIST. POP UP. DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION |
| `cand-f2bb9009e279b8ae` | `S2_llm_schema_slice` | `schema_shaped_object` | `advisoryNumber` | 40 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 1233Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 14/1500Z - 14/2259Z CUMULATIVE PROGRAM PERIOD... |
| `cand-fc2117c984a9dfb9` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | OTHER / OTHER | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |

## ATCSCC-GOLD-038 / 2026-05-20:115

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=115
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD: 20/1700Z - 21/0359Z PROGRAM RATE: 18/18/22/24/24/24/24 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1425 CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB DELAY ASSIGNMENT TABLE APPLIES TO: ZNY MAXIMUM DELAY: 272 AVERAGE DELAY: 97 IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. EFFECTIVE TIME: 201857-210459 SIGNATURE: 26/05/20 18:59 FAA.gov Home \| Privacy Policy \| Web Policies &...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-06191c699e48f767` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-2343b45dcb35ac1a` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | LGA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | CTL ELEMENT: LGA ELEMENT TYPE: APT |
| `cand-290e32085adc8424` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'delay_minutes', 'text': '97'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 97 |
| `cand-3249337ccf78343b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'rate_sequence', 'text': '18/18/22/24/24/24/24'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 18/18/22/24/24/24/24 |
| `cand-37a63ae1ca753176` | `S2_llm_schema_slice` | `schema_shaped_object` | `advisoryNumber` | 115 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-4ab1468cb55b37c9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T18:57:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201857-210459 |
| `cand-4f776ce78dcd2597` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LGA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: LGA |
| `cand-5224d2e7f1e0b61b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'effective_time_range', 'text': '201857-210459'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201857-210459 |
| `cand-5b2ad656d2bc369d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'airport', 'text': 'LGA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LGA |
| `cand-6c0fc5d7403e311c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'flight_scope', 'text': 'ALL CONTIGUOUS US DEP DEP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-7402a3b53f31e4c8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'center', 'text': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZNY |
| `cand-8442ae96d2bd405b` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8f91bd797d69f049` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'delay_assignment_mode', 'text': 'UDP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-90a49e61b944b641` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'time_window', 'text': '20/2100Z - 21/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z |
| `cand-9dd1708be2f83131` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a816b0d3134a86ae` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'airport_and_center_area', 'text': 'LGA/ZNY'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM |
| `cand-aca736b46f46007a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'time_window', 'text': '20/1700Z - 21/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 20/1700Z - 21/0359Z |
| `cand-b8fa90565d768e1d` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T04:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201857-210459 |
| `cand-cdcc39579b4e4052` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'comment', 'text': 'ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS.'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. |
| `cand-ec55c83854e4d643` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. |
| `cand-ed7890f810f14261` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 115 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM |
| `cand-f14fa0474f1f1232` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T18:59:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 18:59 |
| `cand-f16854ef261d2ade` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'airport_list', 'text': 'CYHZ CYOW CYUL CYYZ CYTZ CYQB'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-f789ab6415699714` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'weather_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-fd0952cfc2aac1a1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `unmapped_payload` | {'class_label': 'delay_minutes', 'text': '272'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 272 |

## ATCSCC-GOLD-039 / 2026-05-18:075

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=75
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI RAW TEXT: EVENT TIME: 18/1630 - 18/2230 CONSTRAINED FACILITIES: ZMA THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT. CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS AND ANTICIPATE ALTERNATE ROUTES. ZMA SWAP STATEMENT: SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR ZMA AIRSPACE AND SOUTH FLORIDA TERMINAL AREAS AFTER 1630Z WEATHER CONSTRAINTS: THUNDERSTORMS ARE EXPECTED TO IMPACT SOUTH FLORIDA DEPARTURE AND ARRIVAL ROUTES AND A MAJORITY OF ZMA AIRSPACE. PLANNED ALTERNATE DEPARTURE ROUTES: ALL GATES ARE ANTICIPATED TO BE IMPACTED DUE TO THE NATURE OF...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1689c672871521d9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_reserved_for` | ATC determination | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THESE ROUTES ARE RESERVED FOR ATC DETERMINATION. |
| `cand-1b1257dbaffbe518` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should_not_be_filed` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DO NOT FILE CDR'S THAT END IN 2 OR 3. |
| `cand-1fef9c5ac12be39d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_anticipated_to_be_impacted` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ALL GATES ARE ANTICIPATED TO BE IMPACTED |
| `cand-25942b6f9a8b3481` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:extensionProbability": "MEDIUM", "atm:impactingCondition": "weather", "atm:initiativeComments": "EVENT TIME: 18/1630 - 18/2230 CONSTRAINED FACILITIES:... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-2c9f289f4e38491d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect` | possible playbooks, tactical route adjustments, holding on inbound flights, and ZMA ground stops | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS |
| `cand-2d671de1561d2ce3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_facility` | ZMA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA |
| `cand-2d8b39097b4f782c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_causing` | coded departure routes and/or swaps out of an alternate gate | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO THE NATURE OF THE THUNDERSTORMS CAUSING CODED DEPARTURE ROUTES AND/OR SWAPS OUT OF AN ALTERNATE GATE. |
| `cand-314f07540b2c537d` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"class": "nas:Airport", "iri": "ZMA", "label": "ZMA"}, "atm:impactingCondition": "weather"} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THUNDERSTORMS ARE EXPECTED TO IMPACT SOUTH FLORIDA DEPARTURE AND ARRIVAL ROUTES AND A MAJORITY OF ZMA AIRSPACE. |
| `cand-3bab0654e0bd9e8a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should_anticipate` | alternate routes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATE ALTERNATE ROUTES. |
| `cand-4c27c0796b01a5ff` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"class": "nas:Airport", "iri": "ZMA", "label": "ZMA"}, "atm:implementationStatus": "FYI", "atm:reRouteReason": "WEATHER", "atm:... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT. CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS AND ANTICIPATE ALTERNATE ROUTES. |
| `cand-5c3ef887b1ea9801` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_event_time_window` | 18/1630 - 18/2230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1630 - 18/2230 |
| `cand-63b4ad9e0017005b` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"class": "nas:Airport", "iri": "ZMA", "label": "ZMA"}, "atm:implementationStatus": "FYI", "atm:reRouteReason": "WEATHER", "atm:... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA SWAP_FYI |
| `cand-7754ed577944f824` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"class": "nas:Airport", "iri": "ZMA", "label": "ZMA"}, "atm:implementationStatus": "RQD", "atm:reRouteReason": "WEATHER", "atm:... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DO NOT FILE CDR'S THAT END IN 2 OR 3. THESE ROUTES ARE RESERVED FOR ATC DETERMINATION. |
| `cand-891a08ff35b2f378` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should_fuel_accordingly_for` | possible departure/arrival gate changes, playbooks, tactical reroutes, holding and other traffic management initiatives | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE FUEL ACCORDINGLY FOR POSSIBLE DEPARTURE/ ARRIVAL GATE CHANGES, PLAYBOOKS, TACTICAL REROUTES, HOLDING AND OTHER TRAFFIC MANAGEMENT INITIATIVES |
| `cand-a2090f7460bba9bd` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"class": "nas:Airport", "iri": "ZMA", "label": "ZMA"}, "atm:extensionProbability": "LOW", "atm:impactingCondition": "weather"} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITHIN THE SOUTH FLORIDA TERMINAL AREA. |
| `cand-a54f1dd3c344710d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `cause` | additional departure delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO LIMITED ESCAPE ROUTES. |
| `cand-a8aae1a1fa83c710` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect` | additional departure delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHTS THAT CANNOT FLY MORE THAN 162NM OFFSHORE CAN EXPECT ADDITIONAL DEPARTURE DELAYS |
| `cand-afee96112b5c4f17` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_expected_to_impact` | South Florida departure and arrival routes and a majority of ZMA airspace | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THUNDERSTORMS ARE EXPECTED TO IMPACT SOUTH FLORIDA DEPARTURE AND ARRIVAL ROUTES AND A MAJORITY OF ZMA AIRSPACE. |
| `cand-b8f67136015825b6` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 75 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-bbf91122ea67b79f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_encouraged_to_file` | normal routings | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE NORMAL ROUTINGS |
| `cand-d12cb8901bdde73d` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:extensionProbability": "MEDIUM", "atm:implementationStatus": "FYI", "atm:initiativeComments": "EVENT TIME: 18/1630 - 18/2230 CONSTRAINED FACILITIES: ZM... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `cand-daaba07795655a96` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_for_planning_purposes_only` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-e8403e84053a9c1e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `require` | appropriate over flight permits | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INTERNATIONAL CDR'S REQUIRE APPROPRIATE OVER FLIGHT PERMITS. |
| `cand-ee00af726ff4b76f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_expected_for` | ZMA airspace and South Florida terminal areas after 1630Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR ZMA AIRSPACE AND SOUTH FLORIDA TERMINAL AREAS AFTER 1630Z |
| `cand-f0d47e58655292cb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `affect` | airspace surrounding and within the South Florida terminal area | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITHIN THE SOUTH FLORIDA TERMINAL AREA. |
| `cand-f11a27e3c13cf1fc` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"class": "nas:Airport", "iri": "ZMA", "label": "ZMA"}, "atm:implementationStatus": "FYI", "atm:reRouteReason": "WEATHER", "atm:... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLANNED ALTERNATE ARRIVAL ROUTES: CUSTOMERS CAN EXPECT POSSIBLE PLAYBOOKS, TACTICAL ROUTE ADJUSTMENTS HOLDING ON INBOUND FLIGHTS, AND ZMA GROUND STOPS DUE TO CONVECTIVE WEATHER IMPACTS TO AIRSPACE SURROUNDING AND WITH... |
| `cand-f39b9b720b514440` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_encouraged_to_comply_with` | all ATCSCC route advisories | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. |

## ATCSCC-GOLD-040 / 2026-05-20:197

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=197
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
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
| `cand-12fca6001e102b93` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 197 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-203828594fd89e69` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | MESSAGE: ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-26002cb331bb77dd` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202359-210200 |
| `cand-4f7e354aaf8bf5f4` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'name': 'ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. |
| `cand-569c509ea9558a81` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteType` | INFORMATIONAL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-6c6b16eebbd06998` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 197 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-775d71b7524f30d2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `cancellation_status` | cancelled | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. |
| `cand-86d18f294223df83` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 202359-210200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202359-210200 |
| `cand-8cbe71b592a4ca14` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteReason` | OTHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-8ddf61aa108b2d0b` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T23:59:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 23:59 |
| `cand-903a0e4805f08cec` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-20T23:59:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 23:59 |
| `cand-d0c8701a2fa63300` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-d35d1e5c001b7698` | `S1_llm_only` | `freeform_or_unmapped_fact` | `advisory_message_type` | reroute cancellation | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-e7a52d4d04c90f36` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_remark` | associated restrictions | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-ffda238e74aa07e9` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T23:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202359-210200 |
