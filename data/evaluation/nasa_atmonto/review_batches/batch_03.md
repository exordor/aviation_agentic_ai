# NASA ATMONTO Gold Review batch_03

- Samples: `ATCSCC-GOLD-021` to `ATCSCC-GOLD-030`
- Records: 10
- Candidate clusters: 324

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-021 / 2026-05-14:089

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=89
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 089 BNA/ZME 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2220Z GROUND STOP PERIOD: 14/2112Z - 14/2300Z DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 606 / 70 / 23 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1243 / 100 / 48 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 EFFECTIVE TIME: 142224-150000 SIGNATURE: 26/05/14 22:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b27ba3913cff5eb` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 89 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 089 BNA/ZME 05/14/2026 CDM GROUND STOP |
| `cand-279ebb6249912ae1` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': 'MEDIUM', 'type': 'probability_level'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2b5cf5ccc8559c5d` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2220Z GROUND STOP PERIOD: 14/2112Z - 14/2300Z DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME... | `{"repaired_accepted": 1}` | `{}` | MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2220Z GROUND STOP PERIOD: 14/2112Z - 14/2300Z DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 606 / 70 / 23... |
| `cand-2c543cf5f8578bb1` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EXTENDED UPDATE TIME OF 2300 | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-2d4299187edb5d15` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-2e294cf308c6f3fe` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': '14/2112Z - 14/2300Z', 'type': 'time_period'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 14/2112Z - 14/2300Z |
| `cand-3613697a48cba1f5` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-3fce3a58f4cc7b30` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-47e111d08ed41660` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EXTENDED UPDATE TIME OF 2300 | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-4a1c7dd0530889ee` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': '2300', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-51f018e66b70d674` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': '1243 / 100 / 48', 'type': 'delay_summary'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1243 / 100 / 48 |
| `cand-5c7b313cbd88caca` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': 'APT ADL', 'type': 'element_type'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-69fab0a4e5c06090` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': 'BNA', 'type': 'airport_element'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-75007d05dcb81810` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': 'ZAU ZTL ZHU ZFW ZKC ZME ZID', 'type': 'facility_list'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-7ee7e216e7c5420e` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': '142224-150000', 'type': 'effective_time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 142224-150000 |
| `cand-86fba66a3877c7c0` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-8d509d0f8d6be841` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | nas:Airport:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-96f3039aa7e0a539` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': '606 / 70 / 23', 'type': 'delay_summary'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 606 / 70 / 23 |
| `cand-97f357231cf50a47` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-9abe91116e64a3db` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-9eb32a440b4f66ea` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING |
| `cand-ad2d06e9d1a627d0` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T22:24:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-b9f1b5087c191683` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T22:24:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-c46d5275cfd6c61f` | `S1_llm_only` | `canonical_fact` | `'relation'}` | {'label': 'STAFFING', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-cb09a7d9636ec658` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-f592c62fd6c78f3d` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-14T22:25:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/14 22:25 |

## ATCSCC-GOLD-022 / 2026-05-15:064

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=64
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 41

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1925Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z ANTICIPATED PROGRAM RATE: 32 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1000 CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME ANTICIPATED MAXIMUM DELAY: 53 ANTICIPATED AVERAGE DELAY: 26 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z EFFECTIVE TIME: 151929-152059 SIGNATURE: 26/05/15 19:29 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Con...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-094f22140ae44565` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-1635003ceb0b99ef` | `S1_llm_only` | `canonical_fact` | `anticipated_cumulative_program_period` | 15/2200Z - 16/0029Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z |
| `cand-240145bc3abe741a` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:ARTCC/ZME | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-2de1380890b26b1b` | `S1_llm_only` | `canonical_fact` | `advisory_time` | 1925Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1925Z |
| `cand-3167af0fee031bf1` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport/BNA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-35fc5a5c1bfbe913` | `S1_llm_only` | `canonical_fact` | `arrival_window_estimated_for` | 15/2200Z - 16/0029Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-428492ab62865bde` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport/BNA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-437e61390c681ba5` | `S1_llm_only` | `canonical_fact` | `anticipated_program_rate` | 32 FLT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 32 FLT |
| `cand-4674b836ca5b672a` | `S1_llm_only` | `canonical_fact` | `applies_to` | ZME | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-4a8e16e435b192b5` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-5610e99f038d001e` | `S1_llm_only` | `canonical_fact` | `impacting_condition` | STAFFING | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-57ce8874d3627cb8` | `S1_llm_only` | `canonical_fact` | `announces_ground_delay_program` | CDM PROPOSED GROUND DELAY PROGRAM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-5dcba8ac137fa961` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-67aa9cea399fd7f9` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-15T19:29:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/15 19:29 |
| `cand-6c6bfffe6f08d537` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-6ebc8ed5e864e9bc` | `S1_llm_only` | `canonical_fact` | `effective_time` | 151929-152059 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151929-152059 |
| `cand-6f2b09e40c5a60b5` | `S1_llm_only` | `canonical_fact` | `anticipated_average_delay` | 26 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 26 |
| `cand-7002bfe91f58e99d` | `S2_llm_schema_slice` | `canonical_fact` | `impactingConditionMessage` | STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-7129bee378c8832a` | `S1_llm_only` | `canonical_fact` | `element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-73e4a36d8cfbecf6` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:59:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151929-152059 |
| `cand-781b0734f521568c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:25:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1925Z |
| `cand-879036b514440ee8` | `S1_llm_only` | `canonical_fact` | `canadian_departure_airports_included` | NONE | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-87af7a67a8da3c09` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-15T19:29:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/15 19:29 |
| `cand-8adc4b2b880e8374` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 64 | `{"repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-8d11aae1aaf9f22d` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:29:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151929-152059 |
| `cand-95c98040b6999169` | `S1_llm_only` | `canonical_fact` | `staffing_comment` | PROPOSAL ONLY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-9ad275f55840f42f` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-9b238f9c0e5fec81` | `S1_llm_only` | `canonical_fact` | `must_be_received_by` | 15/2000Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-a9351ea9d710cf21` | `S2_llm_schema_slice` | `canonical_fact` | `type` | atm:GroundDelayProgramTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-b31e727ee7d4e74f` | `S2_llm_schema_slice` | `canonical_fact` | `departureScope` | {'atm:includesAirport': 'all contiguous US departure airports', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-cb27d7fb0cbc0dbf` | `S1_llm_only` | `canonical_fact` | `controlled_terminal_element` | BNA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-d0e000c7a1c4e78c` | `S2_llm_schema_slice` | `canonical_fact` | `departureScope` | {'atm:includesAirport': 'BNA', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-d226ad7515cb8c44` | `S2_llm_schema_slice` | `canonical_fact` | `flightInclusionSpec` | {'description': 'ALL CONTIGUOUS US DEP', 'type': 'atm:FlightSpec'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-d523ea5609a93884` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 64 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-dae06c910c0e4dcf` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-dc95c96f77321922` | `S1_llm_only` | `canonical_fact` | `anticipated_maximum_delay` | 53 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 53 |
| `cand-e664f8d2945ed5ea` | `S1_llm_only` | `canonical_fact` | `conference_time` | 1945Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONFERENCE AT 1945Z |
| `cand-ec8e76da4d160024` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | nas:Airport(BNA) | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT |
| `cand-efc7af5809f60e79` | `S1_llm_only` | `canonical_fact` | `delay_assignment_mode` | UDP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-f3d1f2325bb196fa` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151929-152059 |
| `cand-f541b536ee9bd87f` | `S1_llm_only` | `canonical_fact` | `applies_to_scope` | ALL CONTIGUOUS US DEP | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCL: ALL CONTIGUOUS US DEP SCOPE: 1000 |

## ATCSCC-GOLD-023 / 2026-05-20:163

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=163
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1918 / 74 / 46 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-122d4de55840b5a0` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | urn:nas:Airport:DEN | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT |
| `cand-181e571abb376ae3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T23:15:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIO... |
| `cand-19bae32975f9db4b` | `S1_llm_only` | `canonical_fact` | `'has_control_element'}` | {'label': 'DEN ELEMENT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-1fcdf3d9db300e34` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DEN | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN |
| `cand-2022703c27378dc2` | `S1_llm_only` | `canonical_fact` | `'tier'}` | {'label': '1stTier'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-35319193695116ac` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-40dac55fbb1543a3` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-4eb47e3f307afdd4` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T22:00:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 22:00 |
| `cand-4f36ace149a421c9` | `S1_llm_only` | `canonical_fact` | `'has_element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-5064f1e4079f118a` | `S1_llm_only` | `canonical_fact` | `'announces_ground_stop_period'}` | {'label': 'ground stop period', 'value': '20/2200Z - 20/2315Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-569d84202a0d06f5` | `S1_llm_only` | `canonical_fact` | `'states_probability_of_extension'}` | {'label': 'probability', 'value': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-5d0abfa3cfed7e01` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T22:00:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIO... |
| `cand-5d2ead0d40b104d2` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T22:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 22:00 |
| `cand-77d3481493ee545c` | `S1_llm_only` | `canonical_fact` | `'has_effective_time'}` | {'label': 'effective time', 'value': '202159-210015'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-83c548aa70e78d10` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-842037af82734de0` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | DEN | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-8f91309f1e6d40ec` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-91a2f4da818bd436` | `S1_llm_only` | `canonical_fact` | `'reports_previous_delays'}` | {'label': 'delay statistics', 'value': '0 / 0 / 0'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-9590366ca49fb019` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 163 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-97645fb2b11c349f` | `S1_llm_only` | `canonical_fact` | `'reports_new_delays'}` | {'label': 'delay statistics', 'value': '1918 / 74 / 46'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1918 / 74 / 46 |
| `cand-9d4b45b1cec3fb96` | `S1_llm_only` | `canonical_fact` | `'states_impacting_condition'}` | {'label': 'impacting condition', 'value': 'STAFFING'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-a5aab9c643372e8d` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-a60bed52369f1505` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'departure facilities included', 'value': 'ZLA ZLC ZDV ZKC ZAB ZMP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-a6922b5593037b5a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIO... |
| `cand-c524a918fe25acd9` | `S2_llm_schema_slice` | `canonical_fact` | `withinARTCC` | urn:nas:ARTCCtier:1stTier | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-ca41ec463fbb2a45` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:59:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-cc9e158e5fe5e185` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 163 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-d159a2d13a7436a7` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T00:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202159-210015 |
| `cand-d32a31ca6bfa56fc` | `S2_llm_schema_slice` | `canonical_fact` | `departureScope` | urn:airportSpec:2026-05-20:163:departure | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-e320b7906d19af60` | `S2_llm_schema_slice` | `canonical_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-e3df139d7267390b` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T00:01:15Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-e6b318a76e50badd` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202159-210015 |
| `cand-eefb116bee0bbaa1` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-024 / 2026-05-18:136

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=136
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 34

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2129Z GROUND STOP PERIOD: 18/2130Z - 18/2245Z DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 901 / 75 / 39 PROBABILITY OF EXTENSION: LOW IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09fd167dc50d6c64` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 136 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-138b9c677d8dfbfb` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T21:31:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-17dea59a08effe51` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | STAFFING / STAFFING COMMENTS: | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-1d7f82ec8c1f1ccb` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {'id': 'BNA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT |
| `cand-1e6b560f1675feb5` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZKC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-2340afc035f433b2` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-237c6417370d3960` | `S1_llm_only` | `canonical_fact` | `'effective_during'}` | {'label': '182131-182345'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-33573443e4cd72a6` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZID'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-40d1bfb4d6d4760f` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-4ebcf573704c556b` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZME'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-5712d720d06c60fb` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T21:31:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182131-182345 |
| `cand-571fc9e87c4ce74c` | `S1_llm_only` | `canonical_fact` | `'starts_at'}` | {'label': '18/2130Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-696688b8e2ef844c` | `S1_llm_only` | `canonical_fact` | `'has_control_element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL |
| `cand-6f1563cf130a516a` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-81d918a74dd2f70d` | `S1_llm_only` | `canonical_fact` | `'ends_at'}` | {'label': '18/2245Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-82984cbf2bf25dab` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T23:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182131-182345 |
| `cand-8604f488b9fb2706` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZTL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-89b755fab41c7e7a` | `S1_llm_only` | `canonical_fact` | `'references_air_traffic_facility'}` | {'label': 'ZME'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-8c470008cbd0ad6f` | `S1_llm_only` | `canonical_fact` | `'has_new_delays'}` | {'label': '901 / 75 / 39'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 901 / 75 / 39 |
| `cand-8cb241de1c37c205` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-92413edf53cebf59` | `S1_llm_only` | `canonical_fact` | `'has_previous_delays'}` | {'label': '0 / 0 / 0'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-a815502d2cae7ab2` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZFW'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-a8a086e51688bed5` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T22:45:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-aa3df19feb940e20` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: LOW |
| `cand-add7a13d3997fb37` | `S1_llm_only` | `canonical_fact` | `'announces_ground_stop_for'}` | {'label': 'BNA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-aed512b3ad3e8647` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-c6029b6b4ae79d34` | `S1_llm_only` | `canonical_fact` | `'has_probability_of_extension'}` | {'label': 'LOW'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-d4faf6c27e3dbe69` | `S1_llm_only` | `canonical_fact` | `'has_advisory_time'}` | {'label': '2129Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2129Z GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-df171d1156f63ddd` | `S1_llm_only` | `canonical_fact` | `'has_impacting_condition'}` | {'label': 'STAFFING'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-df5e86e858e0a9f4` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-e1798b2806e8574b` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | LOW | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-e47958f2b535bf04` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZHU'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-e87d81e4d0da674c` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'label': 'ZAU'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-ebe3d7c5dec976c5` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T21:31:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 21:31 |

## ATCSCC-GOLD-025 / 2026-05-18:144

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=144
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DTW ELEMENT TYPE: APT ADL TIME: 2208Z GROUND STOP PERIOD: 18/2126Z - 18/2245Z DEP FACILITIES INCLUDED: (Manual) ZDC PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ZID REMOVED FROM STOP. EFFECTIVE TIME: 182212-182345 SIGNATURE: 26/05/18 22:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09b4e474a08d2632` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport(DTW) | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DTW ELEMENT TYPE: APT |
| `cand-109f1b3288d9b43b` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 144 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |
| `cand-1b46f0fc77e40c48` | `S1_llm_only` | `canonical_fact` | `identifies_controlled_element` | DTW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DTW |
| `cand-2076ca069a700c2a` | `S1_llm_only` | `canonical_fact` | `sets_ground_stop_period` | 18/2126Z - 18/2245Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2126Z - 18/2245Z |
| `cand-23c2e603017cc75e` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T23:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182212-182345 |
| `cand-3390a1931b681bff` | `S1_llm_only` | `canonical_fact` | `reports_new_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-347ce50cf6ec3f4c` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ZID REMOVED FROM STOP. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-5114e03377deefe8` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DTW | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DTW |
| `cand-5f5bf120ae1892ea` | `S1_llm_only` | `canonical_fact` | `states_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-5f9916fb2606922c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T22:12:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-73dd866057e92a76` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T22:34:59Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-8a25a93040e32551` | `S1_llm_only` | `canonical_fact` | `provides_effective_time` | 182212-182345 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-8a4d52f755f8c978` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8a75557726aa8f37` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ZID REMOVED FROM STOP. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-8dec8fee8da6181e` | `S1_llm_only` | `canonical_fact` | `notes_comment` | ZID REMOVED FROM STOP. | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-c216895a26fcfe92` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T22:12:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182212-182345 |
| `cand-d505bc80452fd4f0` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d63611218fb40e69` | `S1_llm_only` | `canonical_fact` | `states_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d73d6d85232e9199` | `S1_llm_only` | `canonical_fact` | `reports_previous_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-db8d40f4b0469e9d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T22:13:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 22:13 |
| `cand-dd7fe42d7e0aa23e` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-e13c0603b93a6dca` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e94505a05e34b884` | `S1_llm_only` | `canonical_fact` | `includes_departure_facility` | ZDC | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC |
| `cand-ea5d486ab82989ee` | `S1_llm_only` | `canonical_fact` | `identifies_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-edfbd49206f32355` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-ee43b07de6fb2501` | `S1_llm_only` | `canonical_fact` | `has_signature_time` | 26/05/18 22:13 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 22:13 |
| `cand-f73d13eae3bcbe7a` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T22:13:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | SIGNATURE: 26/05/18 22:13 |
| `cand-fb2740f204293e4b` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 144 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |
| `cand-fc58c344eb3e64c8` | `S1_llm_only` | `canonical_fact` | `states_action` | GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |

## ATCSCC-GOLD-026 / 2026-05-18:055

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=55
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 31

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 467 / 84 / 52 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-034db367e9d375fd` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T14:13:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181413-181630 |
| `cand-083e3ed6eff857ca` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T14:01:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-0c0cceff9e74d754` | `S1_llm_only` | `canonical_fact` | `has_ground_stop_period` | 18/1401Z - 18/1530Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-1119e9bba0d1f7b6` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-126a8e3c5e6277a6` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1278acf0f5f15423` | `S1_llm_only` | `canonical_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-147a3a2134b37878` | `S1_llm_only` | `canonical_fact` | `has_signature_timestamp` | 26/05/18 14:13 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 14:13 |
| `cand-19b4144d49456889` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-2232b3e06191c950` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 55 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-2c12a9dca07ddad4` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-2f064ad5f77b7020` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-324b120137d8a604` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-32c296f073cc8bda` | `S1_llm_only` | `canonical_fact` | `has_advisory_time` | 1411Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-3bca2d20bb94f614` | `S1_llm_only` | `canonical_fact` | `has_new_total_maximum_average_delays` | 467 / 84 / 52 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 467 / 84 / 52 |
| `cand-4b4e37c2fc8fd5a1` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT |
| `cand-4bd475d0799bc7bc` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 181413-181630 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181413-181630 |
| `cand-51b520b4b1a90fc5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-5b35dc0ac59a8d20` | `S1_llm_only` | `canonical_fact` | `has_advisory_identifier` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-664d400a1c932b83` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6771a5c6cbe85cd9` | `S1_llm_only` | `canonical_fact` | `specifies_control_element` | STL ELEMENT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-6e469dea97c7729e` | `S1_llm_only` | `canonical_fact` | `has_previous_total_maximum_average_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-8bbdaeff5c0419d2` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 181413-181630 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181413-181630 |
| `cand-90d0e1d5258bb093` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-18T14:13:00Z | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | SIGNATURE: 26/05/18 14:13 |
| `cand-a64f6810243d3806` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T16:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181413-181630 |
| `cand-aaceefc344aa46c5` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 55 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-ac9a128f0ab1b7f9` | `S1_llm_only` | `canonical_fact` | `is_impacted_by_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b2eb6cfea87c9b49` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T15:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-baa86ee95e78679d` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-bc1b6c4b8e2dbfe3` | `S1_llm_only` | `canonical_fact` | `includes_departure_facilities` | ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-d39d265249a67f2d` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-df8069f61bcb616f` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T14:13:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:13 |

## ATCSCC-GOLD-027 / 2026-05-19:110

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=110
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 34

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 125 / 43 / 42 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. EFFECTIVE TIME: 192111-192245 SIGNATURE: 26/05/19 21:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-041db9b70938f3b1` | `S1_llm_only` | `canonical_fact` | `has ground stop period` | 19/2058Z - 19/2145Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-1a8aeb85505b7f96` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T20:58:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-21ee2bd00955d6ba` | `S1_llm_only` | `canonical_fact` | `has advisory time` | 2108Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-34a6658fac5f4e71` | `S1_llm_only` | `canonical_fact` | `has element type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-3c4a3bc5521a93f6` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. |
| `cand-4b41f8839fa69951` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T21:08:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-4bb5041e4267edc7` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T21:45:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-5004e9f39e3dcaa2` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T21:12:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:12 |
| `cand-5029b30861d97c10` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 110 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP |
| `cand-5623e511d654b4e4` | `S1_llm_only` | `canonical_fact` | `notes comment` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. |
| `cand-60776eb97d5a0e71` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T22:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192111-192245 |
| `cand-6cfa818bd4ce0bad` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-6f54610c2dc99d3f` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ORD | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-7afbb9bd387419a3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T20:58:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-7c92f4064c779310` | `S1_llm_only` | `canonical_fact` | `reports previous delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-887769b4dc25b79d` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8df6484f32742834` | `S1_llm_only` | `canonical_fact` | `reports new delays` | 125 / 43 / 42 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 125 / 43 / 42 |
| `cand-9d3794e899b6dcdf` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a4a0095be74fb497` | `S1_llm_only` | `canonical_fact` | `states probability of extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a7f6f447b9393f68` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T21:11:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192111-192245 |
| `cand-a986c3ddcebfa716` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-b57bd7640bc45c8d` | `S1_llm_only` | `canonical_fact` | `includes departure facilities` | ZDC ZNY ZOB ZID | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID |
| `cand-b6ea5d2cbbac9287` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-b89038b717fd3e0a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T21:45:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-c2805ce52554d96a` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 110 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-d15659d15eee663d` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-d2ff6eaee5492cb6` | `S1_llm_only` | `canonical_fact` | `names control element` | ORD ELEMENT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-d62e8b14d87ca294` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-d7700b5fb977b9c5` | `S1_llm_only` | `canonical_fact` | `has advisory headline` | ORD/ZAU 05/19/2026 CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP |
| `cand-e07959f6c4bcb619` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | {"evidence_text": "CTL ELEMENT: ORD ELEMENT TYPE: APT", "type": "nas:Airport"} | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT |
| `cand-e0cc34cea7cbb4c2` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-ee82375348b0458c` | `S1_llm_only` | `canonical_fact` | `names impacting condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-f752b6e5b95bfe00` | `S1_llm_only` | `canonical_fact` | `has effective time window` | 192111-192245 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192111-192245 |
| `cand-fe84afe7933e42e9` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |

## ATCSCC-GOLD-028 / 2026-05-18:123

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=123
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 35

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: NO ROUTES EFFECTIVE TIME: 182022-182230 SIGNATURE: 26/05/18 20:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08d1954bd885399d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T20:25:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:25 |
| `cand-09e4c7e007198561` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:22:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182022-182230 |
| `cand-11a622cab58e1040` | `S1_llm_only` | `canonical_fact` | `has_new_total_delay` | 39 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-223627f9f7adef81` | `S1_llm_only` | `canonical_fact` | `has_previous_average_delay` | 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-2909877ace983808` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-3180705419906a34` | `S1_llm_only` | `canonical_fact` | `includes_departure_facility` | ZOB | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-4125941f77efcb3d` | `S1_llm_only` | `canonical_fact` | `announces_ground_stop_for` | MSP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `cand-490a0fe8225fac2c` | `S1_llm_only` | `canonical_fact` | `became_effective_at` | 182022-182230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-4d0ff8823bad4100` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:22:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-5e2f1cfff8539887` | `S1_llm_only` | `canonical_fact` | `has_new_average_delay` | 39 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-5ffebbbf03aebf75` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport:MSP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: MSP ELEMENT TYPE: APT |
| `cand-66456ed62716af4c` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MSP | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP |
| `cand-693735614a3e2887` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182022-182230 |
| `cand-733a50d70b8e6531` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-77ca277b4c5d3335` | `S1_llm_only` | `canonical_fact` | `has_comment` | NO ROUTES | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: NO ROUTES |
| `cand-7b0b7ab29f3078cb` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | MSP | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 3... |
| `cand-7ecc4cb91bfc0471` | `S1_llm_only` | `canonical_fact` | `is_controlled_by` | CTL ELEMENT MSP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z |
| `cand-826af240adb0a231` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-8ea4cb33d45cfb93` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | NO ROUTES | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: NO ROUTES |
| `cand-90a62edcb56ffbd7` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 3... |
| `cand-948713c9bdc22713` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T20:25:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |
| `cand-9ae9e8ac06fa4d18` | `S1_llm_only` | `canonical_fact` | `has_ground_stop_period` | 18/2009Z - 18/2130Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2009Z - 18/2130Z |
| `cand-9bbbec8ae25034dc` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | NO ROUTES | `{"repaired_accepted": 1}` | `{}` | COMMENTS: NO ROUTES |
| `cand-a85b70ddae55179b` | `S1_llm_only` | `canonical_fact` | `has_previous_total_delay` | 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-ae390ab31a84b437` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b14c415e3b61ecc1` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 123 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `cand-b19ec6a1c326993a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 3... |
| `cand-ba8ff158e1a5028b` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-cf42983557624190` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d1d78f2760a13c55` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d52e05122fc668b1` | `S1_llm_only` | `canonical_fact` | `was_signed_at` | 26/05/18 20:25 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |
| `cand-e6ba863cd1d13331` | `S1_llm_only` | `canonical_fact` | `has_previous_maximum_delay` | 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-f01e77005ea9fd6f` | `S1_llm_only` | `canonical_fact` | `has_new_maximum_delay` | 39 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-f256d1d94d4ef553` | `S1_llm_only` | `canonical_fact` | `is_impacted_by_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-f90c0d71e551cd6f` | `S2_llm_schema_slice` | `canonical_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |

## ATCSCC-GOLD-029 / 2026-05-18:001

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=1
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 0000Z GROUND STOP PERIOD: 17/2350Z - 18/0115Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1793 / 77 / 47 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03906a641a66bfc0` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-087d2dff925e74e2` | `S1_llm_only` | `canonical_fact` | `previous_total_maximum_average_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-0b503db0142a4e20` | `S1_llm_only` | `canonical_fact` | `has_ground_stop_period` | 17/2350Z - 18/0115Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 17/2350Z - 18/0115Z |
| `cand-1f5a91f5ef87fa7e` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T00:02:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 00:02 |
| `cand-2583ed8c700d85d6` | `S1_llm_only` | `canonical_fact` | `new_total_maximum_average_delays` | 1793 / 77 / 47 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1793 / 77 / 47 |
| `cand-27ee881772496010` | `S1_llm_only` | `canonical_fact` | `has_advisory_type` | CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP |
| `cand-302828c09cfd87cf` | `S1_llm_only` | `canonical_fact` | `signed_at` | 26/05/18 00:02 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 00:02 |
| `cand-52d08d9789919b18` | `S1_llm_only` | `canonical_fact` | `includes_departure_facilities` | ZLA ZLC ZDV ZKC ZAB ZMP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-57c3d0c16e1edbf4` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DEN | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN |
| `cand-6b87441ef700d2f5` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T02:15:00Z | `{"repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 180001-180215 |
| `cand-77a9d030b4a33bf8` | `S1_llm_only` | `canonical_fact` | `names_control_element` | DEN | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN |
| `cand-7b897dd94631fa93` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-81a8c3284f54564c` | `S1_llm_only` | `canonical_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-82d92daa500dd87a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-99e502e47d1f7724` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | DEN | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 0000Z GROUND STOP PERIOD: 17/2350Z - 18/0115Z |
| `cand-a15e670301cc7cb8` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a4050da616e33f89` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-ad8753f855e364bb` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T00:01:00Z | `{"repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 180001-180215 |
| `cand-b0b2dd035a2cf4d7` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 180001-180215 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180001-180215 |
| `cand-be62ff5679e50508` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THUNDERSTORMS | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d2462e37990fb2e5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d34cc52d495205f8` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e71580455a091361` | `S1_llm_only` | `canonical_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL |
| `cand-fc661d8b2523dc14` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 1 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP |

## ATCSCC-GOLD-030 / 2026-05-16:027

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=27
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 37

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: WORKING ON ROUTES EFFECTIVE TIME: 161146-161330 SIGNATURE: 26/05/16 11:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00869a95ce5ad67b` | `S1_llm_only` | `canonical_fact` | `reports_previous_maximum_delay` | 38 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-0d4d2c8dd1eb27a9` | `S1_llm_only` | `canonical_fact` | `has_ground_stop_period` | 16/1045Z - 16/1230Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-1be7da6faa59aff6` | `S1_llm_only` | `canonical_fact` | `has_control_element` | ORD | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD |
| `cand-23414b3e121bb4a3` | `S1_llm_only` | `canonical_fact` | `states_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-366446e577d2c2b5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-16T11:42:00Z | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z |
| `cand-3786918c3f513e75` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-4528dd0261edf2c7` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T11:46:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 11:46 |
| `cand-4979f9719a1a948a` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T13:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-49850cb65e7a7118` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ORD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-499503d62cf594dc` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-5545df3f73c9ae84` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-67a881b7ce8e3cf0` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T11:46:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 11:46 |
| `cand-68478c5c9e6586e6` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6a70de4757e638b2` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ORD ELEMENT TYPE: APT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAY... |
| `cand-6db911b968c1e246` | `S1_llm_only` | `canonical_fact` | `reports_previous_average_delay` | 26 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-700f4fec55598084` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T11:46:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161146-161330 |
| `cand-79e95d4eef2301a9` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 27 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP |
| `cand-7db1cf02fc0d89e3` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 161146-161330 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-8381c764151965be` | `S1_llm_only` | `canonical_fact` | `reports_previous_total_delays` | 156 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-8468519072327e66` | `S1_llm_only` | `canonical_fact` | `includes_departure_facility` | ZOB | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-893b4c852157e3ca` | `S1_llm_only` | `canonical_fact` | `announces_ground_stop` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CDM GROUND STOP |
| `cand-896eb124e418c6ab` | `S1_llm_only` | `canonical_fact` | `reports_new_maximum_delay` | 78 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-8aa13fe14bbaeea4` | `S1_llm_only` | `canonical_fact` | `reports_new_total_delays` | 403 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-93f87611c5f9e221` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T11:46:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-94850e405ffe9619` | `S1_llm_only` | `canonical_fact` | `identifies_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-9804b4d8db6a2f7d` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | WORKING ON ROUTES | `{"repaired_accepted": 2}` | `{}` | COMMENTS: WORKING ON ROUTES |
| `cand-9f4b484b36df2147` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T12:30:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-aea0686f54cc3c1b` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T11:45:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-b216b2e3879a62ba` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | WORKING ON ROUTES | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: WORKING ON ROUTES |
| `cand-bd95bf6308d35814` | `S0_rule_only, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-bed0902b85c44069` | `S1_llm_only` | `canonical_fact` | `comments_on_route_work` | WORKING ON ROUTES | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: WORKING ON ROUTES |
| `cand-bf82b42e4351c3b2` | `S1_llm_only` | `canonical_fact` | `reports_new_average_delay` | 67 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-d0095831a85453f1` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T13:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161146-161330 |
| `cand-dfa911f4880e0776` | `S1_llm_only` | `canonical_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-e0041a54a76982e0` | `S2_llm_schema_slice` | `canonical_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP |
| `cand-e0453736938ef38a` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-f3742cb71e05b537` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `departureScope` | {"properties": {"atm:includesAirport": [{"evidence_text": "DEP FACILITIES INCLUDED: (Manual) ZOB", "value": "ZOB"}]}, "type": "atm:AirportSpec"} | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
