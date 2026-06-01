# NASA ATMONTO Gold Review batch_03

- Samples: `ATCSCC-GOLD-021` to `ATCSCC-GOLD-030`
- Records: 10
- Candidate clusters: 297

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
- Candidate clusters: 21

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
| `cand-2c543cf5f8578bb1` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EXTENDED UPDATE TIME OF 2300 | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-2d4299187edb5d15` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-3613697a48cba1f5` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-3fce3a58f4cc7b30` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-42d4f1ab8e04f01b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': 'STAFFING', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-4784627ed2d10280` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: BNA", "value": "nas:Airport:BNA"}], "atm:extensionProbability": [{"evidence_text": "PROBABILITY... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-553aa5e0e6b6110f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': 'BNA', 'type': 'airport_element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-7dd3839015c160b2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': '14/2112Z - 14/2300Z', 'type': 'time_period'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 14/2112Z - 14/2300Z |
| `cand-86fba66a3877c7c0` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-986d72f2493510a4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': '2300', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-9abe91116e64a3db` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a6139af3927276b7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': 'APT ADL', 'type': 'element_type'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-abfd75384a96c706` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': '142224-150000', 'type': 'effective_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 142224-150000 |
| `cand-ad2d06e9d1a627d0` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T22:24:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-ced19c1124a96a44` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: BNA", "value": "BNA"}], "atm:controlledNASelement_label": [{"evidence_text": "CTL ELEMENT: BNA... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-d429ab7d61755533` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': 'ZAU ZTL ZHU ZFW ZKC ZME ZID', 'type': 'facility_list'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-dabf2e614b44a357` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': '606 / 70 / 23', 'type': 'delay_summary'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 606 / 70 / 23 |
| `cand-eebcd7b21e3402f8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': '1243 / 100 / 48', 'type': 'delay_summary'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1243 / 100 / 48 |
| `cand-f592c62fd6c78f3d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T22:25:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 22:25 |
| `cand-f86ccf9b2bb564d1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'relation'}` | {'label': 'MEDIUM', 'type': 'probability_level'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-022 / 2026-05-15:064

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=64
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 40

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1925Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z ANTICIPATED PROGRAM RATE: 32 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1000 CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME ANTICIPATED MAXIMUM DELAY: 53 ANTICIPATED AVERAGE DELAY: 26 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z EFFECTIVE TIME: 151929-152059 SIGNATURE: 26/05/15 19:29 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Con...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00e90acc2c46aff3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces_ground_delay_program` | CDM PROPOSED GROUND DELAY PROGRAM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-094f22140ae44565` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-10d96ec331781246` | `S1_llm_only` | `freeform_or_unmapped_fact` | `anticipated_cumulative_program_period` | 15/2200Z - 16/0029Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z |
| `cand-18ef332fa6de5f87` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingConditionMessage` | STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-2354199fb3196cd3` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-15T19:25:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1925Z |
| `cand-274e9c1568078781` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport/BNA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-28b0206b6dd272a2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `delay_assignment_mode` | UDP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-322cddb248592a61` | `S1_llm_only` | `freeform_or_unmapped_fact` | `impacting_condition` | STAFFING | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-3df3e011b6702019` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-465074ac45690f8e` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `departureScope` | {'atm:includesAirport': 'BNA', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-4a8e16e435b192b5` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-54a40e6498a79406` | `S1_llm_only` | `freeform_or_unmapped_fact` | `controlled_terminal_element` | BNA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-56a0bb8a25a6a2bc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time` | 151929-152059 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151929-152059 |
| `cand-57c990128ea8bd4f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 64 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-5b876cd344f7a227` | `S1_llm_only` | `freeform_or_unmapped_fact` | `anticipated_maximum_delay` | 53 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 53 |
| `cand-6a703e8804c3766f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-6c6bfffe6f08d537` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-80d609b823fc9c87` | `S1_llm_only` | `freeform_or_unmapped_fact` | `anticipated_program_rate` | 32 FLT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 32 FLT |
| `cand-82c33aae73d6fffe` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-15T19:29:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/15 19:29 |
| `cand-841623f578e4783a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `conference_time` | 1945Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONFERENCE AT 1945Z |
| `cand-87af7a67a8da3c09` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T19:29:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 19:29 |
| `cand-8adc4b2b880e8374` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 64 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-8d11aae1aaf9f22d` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:29:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151929-152059 |
| `cand-90be6428fe6a1107` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_to_scope` | ALL CONTIGUOUS US DEP | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCL: ALL CONTIGUOUS US DEP SCOPE: 1000 |
| `cand-95c8fe5434011396` | `S1_llm_only` | `freeform_or_unmapped_fact` | `advisory_time` | 1925Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1925Z |
| `cand-9c67897296cdc399` | `S1_llm_only` | `freeform_or_unmapped_fact` | `staffing_comment` | PROPOSAL ONLY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-9cfa977cba914735` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-15T20:59:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151929-152059 |
| `cand-a3e9b3cb439aff19` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport/BNA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-bc55632ff6195554` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_to` | ZME | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-bf719cec38697d72` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM", "value": 64}], "atm:controlledNASelement":... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-c3678915d0008b43` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:ARTCC/ZME | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-cb20e3100d13b2cf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `canadian_departure_airports_included` | NONE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-d2903c5ed6f02cce` | `S1_llm_only` | `freeform_or_unmapped_fact` | `must_be_received_by` | 15/2000Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-dae06c910c0e4dcf` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-dcd603ae9477fdee` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `flightInclusionSpec` | {'description': 'ALL CONTIGUOUS US DEP', 'type': 'atm:FlightSpec'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-e3eacf4b6315169b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `anticipated_average_delay` | 26 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 26 |
| `cand-ea54583054355cb3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `arrival_window_estimated_for` | 15/2200Z - 16/0029Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-f3d1f2325bb196fa` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151929-152059 |
| `cand-fadda7b152fed3dd` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `departureScope` | {'atm:includesAirport': 'all contiguous US departure airports', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-ffa73684c8386a27` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `type` | atm:GroundDelayProgramTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |

## ATCSCC-GOLD-023 / 2026-05-20:163

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=163
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 30

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1918 / 74 / 46 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0fda3f3d8ad1f2a6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_previous_delays'}` | {'label': 'delay statistics', 'value': '0 / 0 / 0'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-1fcdf3d9db300e34` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DEN | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN |
| `cand-35319193695116ac` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-3a4df2700fb846f1` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 163 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-3ab408dd2aa4c41b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | other | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-3ef62793115dd1f5` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `withinARTCC` | urn:nas:ARTCCtier:1stTier | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-40dac55fbb1543a3` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-4eb47e3f307afdd4` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T22:00:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 22:00 |
| `cand-5a11e4ba47cfd728` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'departure facilities included', 'value': 'ZLA ZLC ZDV ZKC ZAB ZMP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-5b2d92a68709a9c4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-5f0129a0dd8715dd` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-21T00:01:15Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-632b6b483854d244` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-20T21:59:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-6ccfd88d88177634` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-70d785c85ff679da` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'tier'}` | {'label': '1stTier'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-83c548aa70e78d10` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-900bf304afe95d10` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | urn:nas:Airport:DEN | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT |
| `cand-90b8666d124a54cb` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-9580173c20bbed62` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_control_element'}` | {'label': 'DEN ELEMENT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-9590366ca49fb019` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 163 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-98eef7aaaf25e6ea` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_ground_stop_period'}` | {'label': 'ground stop period', 'value': '20/2200Z - 20/2315Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-9a278629b0136bd8` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-20T22:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 22:00 |
| `cand-9bb8b9d0c4768e9f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_effective_time'}` | {'label': 'effective time', 'value': '202159-210015'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-9cdc9c45c7237d56` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z", "label": "DEN",... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIO... |
| `cand-a5aab9c643372e8d` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-a76b8e8065ab6ac6` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `departureScope` | urn:airportSpec:2026-05-20:163:departure | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-d159a2d13a7436a7` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T00:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202159-210015 |
| `cand-d535591799bc40ea` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_probability_of_extension'}` | {'label': 'probability', 'value': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d549a5f2022eecd6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_impacting_condition'}` | {'label': 'impacting condition', 'value': 'STAFFING'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-df289b3b779471b1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_new_delays'}` | {'label': 'delay statistics', 'value': '1918 / 74 / 46'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1918 / 74 / 46 |
| `cand-e6b318a76e50badd` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202159-210015 |

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
| `cand-027e60863d2d8a69` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | other | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-07638b33b82ff454` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_probability_of_extension'}` | {'label': 'LOW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-083e31dba83df73b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZHU'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-09fd167dc50d6c64` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 136 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-16d295bff4e00747` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_previous_delays'}` | {'label': '0 / 0 / 0'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-1ab06fe232aceb3e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZAU'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-2ebd80da2f2a4c8a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_ground_stop_for'}` | {'label': 'BNA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-3d810c90aec32ef1` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | LOW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-4aaff018fb2918c5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-4ad9fb2019450b48` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZME'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-4debcde9fe455360` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T22:45:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-5712d720d06c60fb` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T21:31:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182131-182345 |
| `cand-6f1563cf130a516a` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-6fbae072e60fcc73` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | STAFFING / STAFFING COMMENTS: | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-70942418da391d02` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZID'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-72eb83c9fb788e51` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_control_element_type'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL |
| `cand-7e0b89c0824db58d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZKC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-82984cbf2bf25dab` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T23:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182131-182345 |
| `cand-8a72f24b5c0275dd` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T21:31:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-8cb241de1c37c205` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-9ad328424e760cba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_impacting_condition'}` | {'label': 'STAFFING'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-a8a96a549dbf1e16` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'references_air_traffic_facility'}` | {'label': 'ZME'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-aa3df19feb940e20` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: LOW |
| `cand-ab7aadd2fce63d97` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'starts_at'}` | {'label': '18/2130Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-aed512b3ad3e8647` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-b5d159c97ee2abcc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'effective_during'}` | {'label': '182131-182345'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-bcd9793121515e49` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'id': 'BNA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT |
| `cand-d4b9b7c53dbfd207` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'ends_at'}` | {'label': '18/2245Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-d705c0e319b35f75` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZTL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-d9922e03f93572a3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'label': 'ZFW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-df5e86e858e0a9f4` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-e19a6ae58486cf7b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_new_delays'}` | {'label': '901 / 75 / 39'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 901 / 75 / 39 |
| `cand-ebe3d7c5dec976c5` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T21:31:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 21:31 |
| `cand-f08937ba2a64138a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_advisory_time'}` | {'label': '2129Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2129Z GROUND STOP PERIOD: 18/2130Z - 18/2245Z |

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
| `cand-07d85b8f2b874518` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-23c2e603017cc75e` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T23:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182212-182345 |
| `cand-347ce50cf6ec3f4c` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ZID REMOVED FROM STOP. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-35ab1ce14a7171c2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `notes_comment` | ZID REMOVED FROM STOP. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-3ae5ccadc9f56798` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport(DTW) | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | CTL ELEMENT: DTW ELEMENT TYPE: APT |
| `cand-50d84a8e1ded2bee` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T22:34:59Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-5114e03377deefe8` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DTW | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DTW |
| `cand-60f81d8ee01e2311` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-61e0f3e4691849d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6e33bf8f640f13fa` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facility` | ZDC | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC |
| `cand-7f44648dadecfa03` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | ZID REMOVED FROM STOP. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-8a4d52f755f8c978` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-93f73138d8a206fb` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T22:13:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | SIGNATURE: 26/05/18 22:13 |
| `cand-9990d9abd4a24ecf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_action` | GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |
| `cand-9b0c81be09bf5474` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 144 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |
| `cand-9e2e1e106c600164` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_new_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-b12ec9af38d4c46d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `sets_ground_stop_period` | 18/2126Z - 18/2245Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2126Z - 18/2245Z |
| `cand-bf60fc743521189c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_controlled_element` | DTW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DTW |
| `cand-c216895a26fcfe92` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T22:12:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182212-182345 |
| `cand-c3a489f96c99d934` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_signature_time` | 26/05/18 22:13 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 22:13 |
| `cand-c4b22a6742eb51e8` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T22:12:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-c6d05ac7ecd3b3f6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-d35d8fac9fa9e02f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d505bc80452fd4f0` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-db8d40f4b0469e9d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T22:13:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 22:13 |
| `cand-de1b6a9827cc7db6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `provides_effective_time` | 182212-182345 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-edfbd49206f32355` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-ef500813de790cab` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_previous_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-fb2740f204293e4b` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 144 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |

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
| `cand-140ea77b5b8dd41b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-19b4144d49456889` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-259a8e3534eb4e05` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 2}` | `{"unknown_fact_type": 2, "unknown_subject_class": 2}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-324b120137d8a604` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-3d3d0b5d90929f33` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_identifier` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-458756964efe5950` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T15:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-6126bb375d520d42` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | EFFECTIVE TIME: 181413-181630 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181413-181630 |
| `cand-634cd0ec2a04ebda` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 2}` | `{"unknown_fact_type": 2, "unknown_subject_class": 2}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-6521e6bcaeaa61ca` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_impacted_by_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-664d400a1c932b83` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6ea3ae56581ba5b6` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T14:01:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-72386ebab10933d1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_time` | 1411Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-725b2a7d4a3b6eb5` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT |
| `cand-84ae208c101f3400` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-963e818d7a92d3fc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_total_maximum_average_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-987b114f9730474f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `specifies_control_element` | STL ELEMENT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-a64f6810243d3806` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T16:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181413-181630 |
| `cand-aa0b8003bef8df24` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T14:13:00Z | `{"rejected_schema": 2}` | `{"unknown_fact_type": 2, "unknown_subject_class": 2}` | SIGNATURE: 26/05/18 14:13 |
| `cand-aaceefc344aa46c5` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 55 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-b20f5136d860395e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 181413-181630 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181413-181630 |
| `cand-baa86ee95e78679d` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-c3b75a711c71bc89` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 55 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-d39d265249a67f2d` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-df8069f61bcb616f` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T14:13:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:13 |
| `cand-e8416a7d1bb92476` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facilities` | ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-f4411c7bc3a58ed5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_total_maximum_average_delays` | 467 / 84 / 52 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 467 / 84 / 52 |
| `cand-f79d2efdd2e04d60` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-f8048f6a929d9273` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-f8d22cc2e57ebcb8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_ground_stop_period` | 18/1401Z - 18/1530Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-fdf5e67da49eb8bd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_signature_timestamp` | 26/05/18 14:13 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 14:13 |

## ATCSCC-GOLD-027 / 2026-05-19:110

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=110
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 125 / 43 / 42 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. EFFECTIVE TIME: 192111-192245 SIGNATURE: 26/05/19 21:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0a0f04e03adcfddd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `notes comment` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. |
| `cand-1e7c35c281b39487` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has ground stop period` | 19/2058Z - 19/2145Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-23397597043111f0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory time` | 2108Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-317d18b9ee8b3ac2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports previous delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-3c4a3bc5521a93f6` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. |
| `cand-5004e9f39e3dcaa2` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T21:12:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:12 |
| `cand-5029b30861d97c10` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 110 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP |
| `cand-5b43fbaa09cf6d13` | `S2_llm_schema_slice` | `schema_shaped_object` | `advisoryNumber` | 110 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |
| `cand-60776eb97d5a0e71` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T22:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192111-192245 |
| `cand-6c9db5385bd13d9c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports new delays` | 125 / 43 / 42 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 125 / 43 / 42 |
| `cand-6cfa818bd4ce0bad` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-84c958de9010f9f9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states probability of extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-887769b4dc25b79d` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8a7e6b2fe9faa39c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names control element` | ORD ELEMENT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-9d3794e899b6dcdf` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a7f6f447b9393f68` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T21:11:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192111-192245 |
| `cand-b09bdfd7b4ef3112` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes departure facilities` | ZDC ZNY ZOB ZID | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID |
| `cand-b1e1e8e52cf8f8be` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has effective time window` | 192111-192245 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192111-192245 |
| `cand-b3ebce1b57a11c75` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names impacting condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b8e225cb5039f4e2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory headline` | ORD/ZAU 05/19/2026 CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP |
| `cand-d62e8b14d87ca294` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-d90369ff3c88f633` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has element type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERA... |
| `cand-f7b507bac5495a8c` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | {"evidence_text": "CTL ELEMENT: ORD ELEMENT TYPE: APT", "type": "nas:Airport"} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL,... |

## ATCSCC-GOLD-028 / 2026-05-18:123

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=123
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: NO ROUTES EFFECTIVE TIME: 182022-182230 SIGNATURE: 26/05/18 20:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0466587ed8575b06` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_maximum_delay` | 39 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-08d1954bd885399d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T20:25:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:25 |
| `cand-09e4c7e007198561` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:22:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182022-182230 |
| `cand-255e9caf59cf768a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T20:22:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-4325c59089bffcee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_average_delay` | 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-434e76885bc64a0e` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-5de4b49b156e1c27` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_total_delay` | 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-616173e7c6f3b785` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-66456ed62716af4c` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MSP | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP |
| `cand-693735614a3e2887` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182022-182230 |
| `cand-7dffdf799f7e16b3` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-7e8f1a43bf97f84c` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | MSP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 3... |
| `cand-8169ce47c14c6c5d` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | NO ROUTES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | COMMENTS: NO ROUTES |
| `cand-8464d760297607ff` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was_signed_at` | 26/05/18 20:25 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |
| `cand-8672d570df0abde6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_maximum_delay` | 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-9369a8cb63628b62` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport:MSP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: MSP ELEMENT TYPE: APT |
| `cand-971a308d43b916d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-9bbbec8ae25034dc` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | NO ROUTES | `{"repaired_accepted": 1}` | `{}` | COMMENTS: NO ROUTES |
| `cand-ae390ab31a84b437` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b14c415e3b61ecc1` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 123 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `cand-b18a01862de6defa` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_impacted_by_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-ba8ff158e1a5028b` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-bb0fb0b1c75e107f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `cand-c0f2422de310f3e3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces_ground_stop_for` | MSP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `cand-cf1a3ab5ede2c848` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facility` | ZOB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-cf42983557624190` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-da7625d498da582d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_average_delay` | 39 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-dc7e934533d72332` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_ground_stop_period` | 18/2009Z - 18/2130Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2009Z - 18/2130Z |
| `cand-e400912eb1b60d94` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_controlled_by` | CTL ELEMENT MSP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z |
| `cand-eaf6e54465a7cb58` | `S1_llm_only` | `freeform_or_unmapped_fact` | `became_effective_at` | 182022-182230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-f208e88ab5557041` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_comment` | NO ROUTES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: NO ROUTES |
| `cand-f3e1ec6e491e7e8c` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T20:25:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |
| `cand-f4b517b6d04bfebb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_total_delay` | 39 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |

## ATCSCC-GOLD-029 / 2026-05-18:001

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=1
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 23

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
| `cand-0d0004b8c1129c71` | `S1_llm_only` | `freeform_or_unmapped_fact` | `previous_total_maximum_average_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-1d094971818afcf2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_type` | CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP |
| `cand-1f5a91f5ef87fa7e` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T00:02:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 00:02 |
| `cand-3d93623f5707184c` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-3dde3030c2369d8f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `new_total_maximum_average_delays` | 1793 / 77 / 47 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1793 / 77 / 47 |
| `cand-4c32e8fafcc07f7f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_control_element` | DEN | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN |
| `cand-4f36b068efd5396e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `signed_at` | 26/05/18 00:02 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 00:02 |
| `cand-57c3d0c16e1edbf4` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DEN | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN |
| `cand-6b87441ef700d2f5` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T02:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180001-180215 |
| `cand-7af25047971876d4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-7b897dd94631fa93` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-8bdb57610abedbe3` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-8f10b86358cc1c5d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL |
| `cand-9beec6bfe3f76b0e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a4050da616e33f89` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-a653fe5911a0f85e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facilities` | ZLA ZLC ZDV ZKC ZAB ZMP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-ad8753f855e364bb` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T00:01:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180001-180215 |
| `cand-d34cc52d495205f8` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-dc211e4e7055f926` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"evidence_text": "CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 0000Z GROUND STOP PERIOD: 17/2350Z - 18/0115Z", "value": "DEN"},... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-e30f746eb5f3f232` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 180001-180215 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180001-180215 |
| `cand-ef9567a17ae40c7b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_ground_stop_period` | 17/2350Z - 18/0115Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 17/2350Z - 18/0115Z |
| `cand-fc661d8b2523dc14` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 1 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP |

## ATCSCC-GOLD-030 / 2026-05-16:027

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=27
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: WORKING ON ROUTES EFFECTIVE TIME: 161146-161330 SIGNATURE: 26/05/16 11:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0beac754bda5ec61` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_new_total_delays` | 403 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-104cc3c6ced7be17` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_new_average_delay` | 67 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-1ac00c716e29d3d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1da128e9e1c78f27` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-3786918c3f513e75` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-3bb5b7747ecac501` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 161146-161330 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-499503d62cf594dc` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-52d173cc91db20ed` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP |
| `cand-5a9087232d29407c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_previous_average_delay` | 26 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-67a881b7ce8e3cf0` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T11:46:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 11:46 |
| `cand-68478c5c9e6586e6` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-700f4fec55598084` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T11:46:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161146-161330 |
| `cand-766bcf4eb868fd3e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `comments_on_route_work` | WORKING ON ROUTES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: WORKING ON ROUTES |
| `cand-795e30f6348219bc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces_ground_stop` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CDM GROUND STOP |
| `cand-79e95d4eef2301a9` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 27 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP |
| `cand-86b373221d23c73b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | WORKING ON ROUTES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | COMMENTS: WORKING ON ROUTES |
| `cand-876d257c7b512108` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facility` | ZOB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-8d1c0aeedb2f9662` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-9804b4d8db6a2f7d` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | WORKING ON ROUTES | `{"repaired_accepted": 1}` | `{}` | COMMENTS: WORKING ON ROUTES |
| `cand-a8043391ef003282` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | ORD ELEMENT TYPE: APT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAY... |
| `cand-bada66a55999765d` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-16T11:46:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-bb2188cb360dc33e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_previous_total_delays` | 156 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-bbb19b38abf7d062` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element` | ORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD |
| `cand-bd95bf6308d35814` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-c184f0b32740d481` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-16T13:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-cbe64fe7879141bd` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z", "value": "ORD"}... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-cfb8fcd13a83dc0a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_new_maximum_delay` | 78 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-d0095831a85453f1` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T13:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161146-161330 |
| `cand-d5a45be1888708b3` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-16T11:46:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 11:46 |
| `cand-d7d9c30e32564fa7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_ground_stop_period` | 16/1045Z - 16/1230Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-e437f19e8eebce2b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-f3f03a2d7ec84786` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_previous_maximum_delay` | 38 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-f9e2580a5c4e7f28` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
