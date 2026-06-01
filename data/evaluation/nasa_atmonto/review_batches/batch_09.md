# NASA ATMONTO Gold Review batch_09

- Samples: `ATCSCC-GOLD-081` to `ATCSCC-GOLD-090`
- Records: 10
- Candidate clusters: 204

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-081 / 2026-05-18:023

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=23
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LAS ELEMENT TYPE: APT ADL TIME: 0615Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 18/0615Z - 18/0759Z CUMULATIVE PROGRAM PERIOD: 18/0056Z - 18/0759Z PROGRAM RATE: 32 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1400 CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZLA MAXIMUM DELAY: 893 AVERAGE DELAY: 232 IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. EFFECTIVE TIME: 180619-180859 SIGNATURE: 26/05/18 06:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word V...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0284f9aa37d26567` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_title` | CDM GROUND DELAY PROGRAM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM |
| `cand-06c5594d180b69ca` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 23 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM |
| `cand-2f1f25dc4a84510d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_comment` | ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-303b1eb0f63923f3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_impacting_condition` | WEATHER / WIND | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / WIND |
| `cand-39d8de17fa355869` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_delay_assignment_mode` | UDP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-44dc9c7a3d3dd2fe` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_program_rate` | 32 FLT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 32 FLT |
| `cand-4d2188d661510e03` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / WIND | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / WIND |
| `cand-61f32e6219962f84` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_maximum_delay` | 893 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 893 |
| `cand-67718b49fb0b21da` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T08:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180619-180859 |
| `cand-764764dad1260d9b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_delay_assignment_table_applies_to` | ZLA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZLA |
| `cand-77d6fcd1cf4883fe` | `S1_llm_only` | `freeform_or_unmapped_fact` | `issued_by` | FAA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FAA Home |
| `cand-893cae2a721a23ef` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T06:20:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 06:20 |
| `cand-8b6840ed487c037a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_cumulative_program_period` | 18/0056Z - 18/0759Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 18/0056Z - 18/0759Z |
| `cand-92120e86710e14e0` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-9fe990fccb70e129` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 180619-180859 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180619-180859 |
| `cand-b1667b23db242d34` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_average_delay` | 232 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 232 |
| `cand-b18ae3c5545fee5b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_adl_time` | 0615Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 0615Z |
| `cand-b69879f4d11833eb` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: LAS ELEMENT TYPE: APT ADL TIME: 0615Z", "value": {"label": "LAS", "type": "nas:Airport"}}], "at... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-b6fcffb3f5ed516f` | `S2_llm_schema_slice` | `schema_shaped_object` | `advisoryNumber` | 23 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM ... IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-c2e47a4486b88f7d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_departure_scope` | 1400 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SCOPE: 1400 |
| `cand-c6486fd143c60f45` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_canadian_departure_airports_included` | NONE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-cd098a71188199d5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_estimated_arrival_window` | 18/0615Z - 18/0759Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 18/0615Z - 18/0759Z |
| `cand-d460a6c50a36a26e` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T06:19:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180619-180859 |
| `cand-db0a466af3cd0d45` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_included_departure_scope` | ALL CONTIGUOUS US DEP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCL: ALL CONTIGUOUS US DEP |
| `cand-eefef68a6bc657cf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element` | LAS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS |
| `cand-f7921ff9723ec760` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / WIND |
| `cand-f9cdbd72b7b91f88` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-fa451639c54a8036` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: LAS |

## ATCSCC-GOLD-082 / 2026-05-20:145

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=145
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000 PROBABILITY OF EXTENSION: LOW REMARKS: REPLACES ADVZY 143 ASSOCIATED RESTRICTIONS: MODIFICATIONS: ARRIVALCHANGED TO JOVEM/HERBZ ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- ZDV >LAA ZLC >JNC HBU PUB LAA ZLC >HVE J28 PUB LAA ZOA >MLF J28 PUB LAA TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KDAL LAA MMB FILGO HYDES < HERBZ2 KDFW LAA MMB MDANO < JOVEM6 TMI ID: RRDCC525 EFFECTIVE TIME: 202...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0029f11e5e1bfebe` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `extensionProbability` | LOW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-09db25e6297e25e3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `destination_route_segments` | LAA MMB MDANO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | HERBZ2 KDFW LAA MMB MDANO |
| `cand-1122886ef965481b` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 145 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-29a122a813173063` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-3d8fb1bd5394bbaf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `destination_route_for` | KDFW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | HERBZ2 KDFW LAA MMB MDANO |
| `cand-4476b4890557dc6c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `destination_route_for` | KDAL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KDAL LAA MMB FILGO HYDES |
| `cand-51809e12d7866d14` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_facilities` | ZDV/ZFW/ZKC/ZLC/ZOA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA |
| `cand-57aa4cd9e2c9396e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-6eef3f6ffe37dac3` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202100-210000 |
| `cand-74a813b6a0b05cd4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `origin_route_segments` | ZDV >LAA; ZLC >JNC HBU PUB LAA; ZLC >HVE J28 PUB LAA; ZOA >MLF J28 PUB LAA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- ZDV >LAA ZLC >JNC HBU PUB LAA ZLC >HVE J28 PUB LAA ZOA >MLF J28 PUB LAA |
| `cand-75b4766ce3eacf9c` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202100-210000 |
| `cand-7ac94e0009c016bc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_name` | DFW_NO_DOGS_HEAD_PARTIAL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL |
| `cand-8e1d1b4c3eb390f3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | LOW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-9de6d4cd8e335215` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_area` | ZAB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZAB |
| `cand-9f51490c3a790884` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T21:12:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:12 |
| `cand-a541461e0e691032` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 145, "atm:allowedRoute": [{"@type": "atm:ReRouteSegment", "atm:implementationStatus": "RQD", "atm:reRouteType": "ROUTE", "evidence_tex... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-b6a2eecf6fe967d9` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: LOW |
| `cand-bc6c07d5778367b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_modification` | ARRIVALCHANGED TO JOVEM/HERBZ | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: ARRIVALCHANGED TO JOVEM/HERBZ |
| `cand-dfa0cddc1744466b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `destination_route_segments` | LAA MMB FILGO HYDES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KDAL LAA MMB FILGO HYDES |
| `cand-dfa23d9cd8b67c22` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time` | 202100-210000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202100-210000 |
| `cand-dfbd0aa40d41bade` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_traffic` | ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW |
| `cand-dfdb44b25e6d321b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `replaces_advisory` | ADVZY 143 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REPLACES ADVZY 143 |
| `cand-f916dac8e320e788` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_valid_window` | ETD 202100 TO 210000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 202100 TO 210000 |
| `cand-f9a4646cec26168f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `arrival_route_name` | JOVEM6 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | JOVEM6 TMI ID: RRDCC525 |
| `cand-fec8b4e97af9ea6d` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `effectiveEndTime` | 2026-05-20T21:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |

## ATCSCC-GOLD-083 / 2026-05-20:016

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=16
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA REMARKS: DAL AND SUBS GS CX. EFFECTIVE TIME: 200052-200200 SIGNATURE: 26/05/20 00:52 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-12ae48ce67c06682` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:52:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200052-200200 |
| `cand-12ebe7f7aef39e99` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'DAL AND SUBS GS CX.'}` | {'label': 'ground stop cancellation for DAL and subsidiaries', 'text': 'DAL AND SUBS GS CX.'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: DAL AND SUBS GS CX. |
| `cand-2506d998077d70a8` | `S2_llm_schema_slice` | `property_bundle` | `withinARTCC` | {"nas:withinARTCC": "ZNY"} | `{"rejected_schema": 2}` | `{"unknown_fact_type": 2, "unknown_predicate": 2, "unknown_subject_class": 2}` | DESTINATION AIRPORT: LGA AND JFK |
| `cand-3054bbc7bd01a0b9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS'}` | {'label': 'ground stop cancellation for DAL and subsidiaries', 'text': 'LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-50f739da369feecc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'20/0050 - 20/0130'}` | {'label': 'event time window', 'text': '20/0050 - 20/0130'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/0050 - 20/0130 |
| `cand-5b0bc4c27c60d7e6` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-5fc517b2133ea8c6` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 16, "atm:controlledNASelement": "nas:Airport", "atm:effectiveEndTime": "2026-05-20T02:00:00", "atm:effectiveStartTime": "2026-05-20T00... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-83d8d74dd9b315c1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'05/20/2026'}` | {'label': '2026-05-20', 'text': '05/20/2026'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-8b34c4ef340ab531` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'200052-200200'}` | {'label': 'effective time window', 'text': '200052-200200'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200052-200200 |
| `cand-8eb6d4ef3d5815b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA'}` | {'label': 'released facilities list', 'text': 'ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RELEASED FACILITIES: ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA |
| `cand-9b746ed1110235c7` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-af97dfcc33e30d46` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-d01eed29cbdb034c` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 16 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-d0784fa4f9831857` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'LGA AND JFK'}` | {'label': 'LGA and JFK', 'text': 'LGA AND JFK'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DESTINATION AIRPORT: LGA AND JFK |
| `cand-eb197e85d719967a` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200052-200200 |
| `cand-f92cdeb325d0f5bf` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T00:52:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:52 |
| `cand-fd75360441c5666c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'ZNY'}` | {'label': 'ZNY', 'text': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |

## ATCSCC-GOLD-084 / 2026-05-17:017

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=17
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 30

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI MESSAGE: EVENT TIME: 17/1900 - 18/0200 CONSTRAINED FACILITIES: ZNY THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT, CUSTOMERS ARE ENCOURAGED TO FILE PUBLISHED CDR'S AND NRP PROCEDURES AROUND KNOWN FORECASTED WEATHER. THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. SWAP STATEMENT: **MORNING FORECAST** SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-2f3a9f30f2e0091f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `encourages_compliance_with` | all ATCSCC route advisories | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. |
| `cand-35b2bae29fdd3012` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_constrained_facility` | ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-3c8030a106f94842` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SWAP STATEMENT: **MORNING FORECAST** SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). |
| `cand-45b41d7dec2a2864` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | FYI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-4692e1d165f39990` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 17 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-48356baef1c9b000` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T11:40:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171140-180230 |
| `cand-4be5b701d6b8d1ba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `describes_swap_as_possible` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SWAP IS POSSIBLE |
| `cand-598b728a43b9bb0d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `will_provide_alternate_routes_to_destinations` | ATL/CLT/MDW/ORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. |
| `cand-5e395104db4ee687` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. |
| `cand-6b45a9f0d2b57aa2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `impact_status` | not_expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INTERNATIONAL DEPARTURES ( EAST GATES ) IMPACTS ARE: NOT EXPECTED |
| `cand-6bfaf1c1d5790273` | `S1_llm_only` | `freeform_or_unmapped_fact` | `possible_active_time` | AFT ( XXX )Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY HOTLINE POSSIBLE AFT ( XXX )Z: 540-359-3200 PIN #2778 |
| `cand-79ebdb3be1881c48` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_destinations_to_file_normal_routes` | ATL/CLT/MDW/ORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. |
| `cand-7d6a06527a6e992b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time` | 171140-180230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171140-180230 |
| `cand-8232d58255548d75` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_weather_avoidance_plans_as_possible` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) |
| `cand-8f75789b290e05d8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expects_impact_area` | ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. |
| `cand-97b272c0008f7a3e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `impact_status` | not_expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AZEZU-PAEPR-HANRI ( L453-Y493 ) IMPACTS ARE: NOT EXPECTED |
| `cand-a187c11851a016a0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `will_provide_reroutes_or_CDRs_as_necessary` | True | `{"rejected_schema": 3}` | `{"unknown_fact_type": 3, "unknown_predicate": 3, "unknown_subject_class": 3}` | POSSIBLE REROUTES / CDR'S WILL BE PROVIDED AS NECESSARY. |
| `cand-ab3ef1e8545a2aa6` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171140-180230 |
| `cand-b4ea1881ab51606d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_have_additional_reroutes_for_effected_airways_outside_ZNY` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDITIONAL DEPARTURE REROUTES MAY BE POSSIBLE FOR IMPACTS TO EFFECTED AIRWAYS OUTSIDE ZNY. |
| `cand-b52f70882d432654` | `S1_llm_only` | `freeform_or_unmapped_fact` | `recommends_published_CDR_and_NRP_use_when_no_route_advisories` | file published CDR's and NRP procedures around known forecasted weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT, CUSTOMERS ARE ENCOURAGED TO FILE PUBLISHED CDR'S AND NRP PROCEDURES AROUND KNOWN FORECASTED WEATHER. |
| `cand-bc4c7bda028ae617` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_impacts_to_j6_q75_and_dc_metros` | possible | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTS TO J6-Q75 & DC METROS PSBL. |
| `cand-cac875604b20bd05` | `S1_llm_only` | `freeform_or_unmapped_fact` | `impact_status` | not_expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DITCH IMPACTS ARE: NOT EXPECTED |
| `cand-d0f561a6e254967d` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-df3fd7d598195e62` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteType` | MISCELLANEOUS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-e517738b1c4920fc` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteReason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-e78bd36f7f00c757` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_planning_purpose_only` | True | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-f12e33d7e0348f8d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `specifies_area_and_time` | ZNY area today/ after ( 19Z ) | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). |
| `cand-f2602070fad5a455` | `S0_rule_only` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | _FYI |
| `cand-f4acd7d8dd0dfc99` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T11:40:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 11:40 |
| `cand-f56ba3afdb7751ec` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. |

## ATCSCC-GOLD-085 / 2026-05-19:009

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=9
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 15

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 190306 WSI DDS:190307 VA ADVISORY DTG: 20260519/0306Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0004 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/493 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 19/0250Z EST VA CLD: SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07740 - N0000 W07751 - N0004 W07748 MOV NW 15KT FCST VA CLD +6HR: 19/0900Z SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07740 - N0000 W07751 - N0004 W07748 FCST VA CLD +12HR: 19/1500Z SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07739 - N0000 W07751 - N0004 W07748 FCST VA CLD +18HR: 19/2100Z...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02310dee4882117b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is not detected due to'}` | {'label': 'weather clouds in summit area', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-217bc004c8b2a3b2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'moves northwest at'}` | {'label': '15 kt', 'type': 'speed'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 15KT |
| `cand-26e8d0d5940288ce` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 9 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-60db28cff5ef34bb` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR", "value": 9}], "atm:effectiveEndTime": [{... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-6e2b0687c9414f2a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has source area'}` | {'label': 'Ecuador', 'type': 'country'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-89716f315ffa10d3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has no change forecast for'}` | {'label': 'next 18 hours', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-9003dfd33e1e959b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is observed from'}` | {'label': 'surface to flight level 140', 'type': 'vertical_extent'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 |
| `cand-90962e52f41ddc70` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T03:06:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:07 |
| `cand-90fa598aad9a3a71` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 009", "value": 9}], "atm:effectiveEndTime": [{"evidence_text": "EFFECTIVE TIME:\n190000-190000", "val... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-91830c04ccab16b7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports eruption details'}` | {'label': 'ongoing volcanic ash emissions', 'type': 'eruption_state'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING VA EMS |
| `cand-9db736f91d3d6579` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-a68a6c7d11bebb55` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'likely continue'}` | {'label': 'recent activity', 'type': 'activity'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-bd516a5422c05dd4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names volcano'}` | {'label': 'Reventador', 'type': 'volcano'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-c7f7211b37c4263f` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-d75610522e958b1f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has source elevation'}` | {'label': '11686 ft AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |

## ATCSCC-GOLD-086 / 2026-05-16:046

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=46
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY MESSAGE: FVAK21 PAWU 161536 WSI DDS:161538 VA ADVISORY DTG: 20260516/1536Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5558 E16035 AREA: KAMCHATKA SOURCE ELEV: 9455 FT AMSL ADVISORY NR: 2026/001 INFO SOURCE: TOKYO VAAC. ERUPTION DETAILS: NOT PROVIDED OBS VA DTG: NOT PROVIDED OBS VA CLD: NOT PROVIDED FCST VA CLD +6HR: 16/2100Z NOT PROVIDED FCST VA CLD +12HR: 17/0300Z NOT PROVIDED FCST VA CLD +18HR: 17/0900Z NOT PROVIDED RMK: PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. ...GATLING EFFECTIVE TIME: 160000-160000 SIGNATURE: 26/05/16 15:38 FAA.gov Home \|...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01ce2278b43e408c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_forecast_volcanic_ash_cloud_plus_18_hours` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 17/0900Z NOT PROVIDED |
| `cand-024dea5b690d9aa3` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-16T16:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160000-160000 |
| `cand-0b363d1a5694336b` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T15:36:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 15:38 |
| `cand-1f074debb1b70cb5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_forecast_volcanic_ash_cloud_plus_12_hours` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 17/0300Z NOT PROVIDED |
| `cand-1f2d5d450281345e` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 46 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-207cea566a6db27f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 46 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 046 |
| `cand-2332865318bc0e2f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-16T15:38:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 15:38 |
| `cand-47fab5cfa64f2391` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_information_source` | TOKYO VAAC | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: TOKYO VAAC. |
| `cand-5ca595319c7fcd48` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_subject_line` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-5ef89b4aed6e2d40` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_observed_volcanic_ash_datetime` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: NOT PROVIDED |
| `cand-666b50307ce44adb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_issued_datetime` | 20260516/1536Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260516/1536Z |
| `cand-70e96a1070ca8c90` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_eruption_details` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: NOT PROVIDED |
| `cand-7256a2eaac9ce875` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-863d87f189fa9a7d` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-16T16:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160000-160000 |
| `cand-867d45fb43613d03` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-8c0eeba2b5d942cb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_observed_volcanic_ash_cloud` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: NOT PROVIDED |
| `cand-9a9aef90aa6fd0d0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time_window` | 160000-160000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160000-160000 |
| `cand-c5d488d378858983` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-c8737bfb08fefda0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_remarks` | PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. |
| `cand-d3b0993359c2d8c2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_in_area` | KAMCHATKA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA |
| `cand-ebe0e3940434032b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_volcano` | BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: BEZYMIANNY |
| `cand-ed54837884795ca8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `cites_advisory_number` | 2026/001 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/001 |
| `cand-f3f8edb84e10de7e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_forecast_volcanic_ash_cloud_plus_6_hours` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/2100Z NOT PROVIDED |
| `cand-f6c996239291ae70` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_position` | N5558 E16035 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5558 E16035 |
| `cand-fd2f35a2991ab6bf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_source_elevation` | 9455 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 9455 FT AMSL |

## ATCSCC-GOLD-087 / 2026-05-18:107

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=107
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 18

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. EFFECTIVE TIME: 181933-190230 SIGNATURE: 26/05/18 19:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0c47e11658807fc0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_affected_departure_airports_scope` | departure airports within the first tier facilities | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES |
| `cand-12a2daffaa515ee4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_effective_time` | 181933-190230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181933-190230 |
| `cand-2f41e064a77803df` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `advisoryNumber` | 107 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-3b0044c7ec92e18a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_delay_duration_range` | 30 TO 45 MINUTES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-5150ad176316c97b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_type` | DEN airport scheduling delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-55116fa027f5c714` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181933-190230 |
| `cand-5abadb3ca4e015bd` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. |
| `cand-7c637423ca7268bd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_delay_type` | TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-8a7341123a75021a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_to_center` | ZDV | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-8aa8f25ca3ac52c6` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'DENVER AIRPORT', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-91700a75a88dc84d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T19:33:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 19:33 |
| `cand-9e5edede9f38e4c2` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T19:33:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181933-190230 |
| `cand-a44fbeddf1fa9c88` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_expected_delay_for` | DENVER AIRPORT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-b3734940a709d5a6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_constrained_facilities` | ZDV | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-c6d119a16dd0976d` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T19:33:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 19:33 |
| `cand-d15b9da1c8d200b8` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atcscc_advisory_text_type": "TBFM / CALL-FOR-RELEASE scheduling delays", "effectiveEndTime": "2026-05-19T02:30:00", "effectiveStartTime": "2026-05-18T19:33... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30... |
| `cand-e5a8e25288a46425` | `S1_llm_only` | `freeform_or_unmapped_fact` | `describes_event_time` | 18/2045 - 19/0200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/2045 - 19/0200 |
| `cand-ec55f7cd15ea3061` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 107 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |

## ATCSCC-GOLD-088 / 2026-05-18:021

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=21
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 18

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EFFECTIVE TIME: 180507-180945 SIGNATURE: 26/05/18 05:07 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1234796b86cf4cd4` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR D... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-20196dc48893017c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `named_airport_element` | SFO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-29a66fccccd701dd` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 21 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-5b0410362e1c3f84` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 21, "atm:controlledNASelement": {"label": "SFO", "type": "nas:Airport"}, "atm:effectiveEndTime": "2026-05-18T09:45:00Z", "atm:effectiv... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-5d6dd40513761b6f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announced_advisory_topic` | CDM GROUND DELAY PROGRAM CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-64b13dde3764a444` | `S1_llm_only` | `freeform_or_unmapped_fact` | `comment` | OBJECTIVES MET | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-6ca82448758304c4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `ground_delay_program_period` | 18/0503Z - 18/0845Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-8a54b2fe15138067` | `S1_llm_only` | `freeform_or_unmapped_fact` | `advisory_time` | 0503Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-8e1da0077d9d3634` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T05:07:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180507-180945 |
| `cand-a02c2cb6316bc6fe` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announced_advisory_area` | SFO/ZOA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-a3c158e4b84efe87` | `S1_llm_only` | `freeform_or_unmapped_fact` | `ground_delay_program_status` | CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-b045ba6031a417c3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `instruction` | DISREGARD EDCTS FOR DEST SFO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-c152438b1f916c03` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-db306c36ca46a977` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T05:07:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 05:07 |
| `cand-e73c075e55611c50` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_interval` | 180507-180945 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180507-180945 |
| `cand-f4357847596acd43` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | OBJECTIVES MET | `{"repaired_accepted": 1}` | `{}` | COMMENTS: OBJECTIVES MET |
| `cand-f5a409d65132ec87` | `S1_llm_only` | `freeform_or_unmapped_fact` | `element_type` | APT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-f5f8bd554146d954` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T09:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180507-180945 |

## ATCSCC-GOLD-089 / 2026-05-16:018

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=18
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 18

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION MESSAGE: EVENT TIME: 16/0915 - 17/0200 THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. EFFECTIVE TIME: 160909-170200 SIGNATURE: 26/05/16 09:09 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-2180ab82d6e2b4de` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T09:09:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160909-170200 |
| `cand-2c1e71ff536de320` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION", "value": 18}], "atm:effective... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-303d69ca72ee66c3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces issue request page activation` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-389507348d1d9984` | `S1_llm_only` | `freeform_or_unmapped_fact` | `status` | now open | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. |
| `cand-3ea198339eb648bc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should send` | request messages to the page for resolution | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. |
| `cand-41385e5cee01b096` | `S1_llm_only` | `freeform_or_unmapped_fact` | `ends at` | 170200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160909-170200 |
| `cand-696f9b21b7875a7c` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T09:09:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 09:09 |
| `cand-8ac3879524abe08c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should include` | position of flight | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-90083d6f8b23e2ee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `runs from` | 16/0915 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-9351bd9d0ee59c07` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should include` | type of assistance requested | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-94e474a342fa80e3` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 18 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-a7f52e8498a256ef` | `S1_llm_only` | `freeform_or_unmapped_fact` | `runs until` | 17/0200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-bd5580d2ad7c4195` | `S1_llm_only` | `freeform_or_unmapped_fact` | `purpose` | to eliminate any misinterpretation | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-c17da2fbf0a440c7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory identifier` | 018 DCC 05/16/2026 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-d1722ab15ead4805` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should include` | category of issue | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-dc9f0d89c9f2860a` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T02:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160909-170200 |
| `cand-f49dd86cd211208a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should include` | call sign | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-fb5989e5e34198e6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `starts at` | 160909 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160909-170200 |

## ATCSCC-GOLD-090 / 2026-05-15:061

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=61
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 10

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0bc981cc0f21ab97` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 61 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-13ba8e6759eebce8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 151849-152030 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151849-152030 |
| `cand-2660aecd99140305` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_status` | cancelled | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. |
| `cand-316a06738bbac3c8` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 61, "atm:controlledNASelement": {"evidence_text": "FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCI... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-3af249d39ed4b06c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `message_type` | reroute cancellation | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION |
| `cand-6b1b80bd23a8554d` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 61 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION |
| `cand-a4f275de0537c1bb` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T18:49:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 18:49 |
| `cand-b000cf7eca091ea4` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151849-152030 |
| `cand-df70688424f6059b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `cancels_reference_advisory` | ADVZY 024 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: |
| `cand-e9329b80d227d255` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T18:49:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151849-152030 |
