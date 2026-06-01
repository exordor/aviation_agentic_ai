# NASA ATMONTO Gold Review batch_05

- Samples: `ATCSCC-GOLD-041` to `ATCSCC-GOLD-050`
- Records: 10
- Candidate clusters: 183

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-041 / 2026-05-18:054

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=54
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 18

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. EFFECTIVE TIME: 181357-181630 SIGNATURE: 26/05/18 13:57 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-06c45d836eb4653c` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-17318a6a0c6a8ef0` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T13:57:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181357-181630 |
| `cand-2bb4e4520aa10aeb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'should_file'}` | {'label': 'alternate routing', 'type': 'routing_action'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-2cfeb9fe98b30060` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 54 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-4100db9c1d5280c2` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | CONSTRAINED FACILITIES: ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-49a271f65979f53d` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-5949af7ce0970381` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | EVENT TIME: 18/1130 - 18/1600 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1130 - 18/1600 |
| `cand-5c45f237fb294308` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T16:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181357-181630 |
| `cand-5fdcb87336f195c7` | `S2_llm_schema_slice` | `schema_shaped_object` | `advisoryNumber` | 54 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-6dd1b3074e24b3e4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is_closed_due_to'}` | {'label': 'thunderstorms', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-851eb7d5e3a2255b` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-996974a5a817431f` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | SIGNATURE: 26/05/18 13:57 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 13:57 |
| `cand-9bf2931ad8cceb23` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'replaces'}` | {'label': 'advisory 035', 'type': 'advisory'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES ADVZY 035*** |
| `cand-b0d0a176accf52ca` | `S0_rule_only` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | _RQD |
| `cand-b4ed693eb027f1d3` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | USERS SHOULD FILE ALTERNATE ROUTING. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-cbc65effd4544927` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'constrains_facility'}` | {'label': 'ZNY', 'type': 'facility'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-f171c5b3be5c5eb6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'removes'}` | {'label': 'L455', 'type': 'route'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *REMOVES L455* |
| `cand-f43b03e61ed3f6cc` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T13:57:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 13:57 |

## ATCSCC-GOLD-042 / 2026-05-20:015

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=15
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 15

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. EFFECTIVE TIME: 200051-200330 SIGNATURE: 26/05/20 00:51 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09cbe3417229ba21` | `S1_llm_only` | `freeform_or_unmapped_fact` | `advises_route_status` | L451 is closed due to thunderstorms | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-2d32195c080d1450` | `S0_rule_only` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | _RQD |
| `cand-36195c5046792989` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:51:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200051-200330 |
| `cand-3b18b9893e52b502` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_effective_time` | 200051-200330 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200051-200330 |
| `cand-4672720305d9c15e` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 15 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-59d15b24b4437ab7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `replaces_advisory` | 136 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *REPLACES ADVISORY 136 |
| `cand-7fe63eb0694fd0ca` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 15, "atm:controlledNASelement": [{"label": "ZMA", "type": "nas:ARTCC"}], "atm:implementationStatus": "RQD", "atm:initiativeComments":... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-a3f27863bc67c9db` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T03:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200051-200330 |
| `cand-aba622133f155c92` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_facility` | ZMA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA |
| `cand-acc979ed4438cecb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_identifier_text` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-b3195c93042d0a63` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_encouraged_to_file` | alternate routes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. |
| `cand-c58104ff8a8859b2` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T00:51:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:51 |
| `cand-c591d564d4db225d` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"label": "ZMA", "type": "nas:Airport"}, "atm:implementationStatus": "RQD", "atm:reRouteReason": "WEATHER", "atm:reRouteType": "... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-eddfce3051907b68` | `S1_llm_only` | `freeform_or_unmapped_fact` | `extends_time_for_route` | L451 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | **EXTENDS TIME FOR L451 |
| `cand-fb92e319109eae89` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_event_time` | 19/2200 - 20/0300Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/2200 - 20/0300Z |

## ATCSCC-GOLD-043 / 2026-05-19:008

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=8
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 10

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 190302-191230 SIGNATURE: 26/05/19 03:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-238f7cc771bf9b6f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'shows_effective_time_as'}` | {'label': '190302-191230', 'type': 'effective_time_string'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190302-191230 |
| `cand-344a908084f683a9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'instructs_use_of'}` | {'label': 'normal ATCSCC phone lines', 'type': 'phone_lines'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-3c0fdd08bc6492ae` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 8, "atm:effectiveEndTime": "2026-05-19T12:30:00", "atm:effectiveStartTime": "2026-05-19T03:00:00", "atm:initiativeComments": "EVENT TI... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER AS... |
| `cand-7ba39ef03c0204b1` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 8 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| `cand-bc174b0c0114647e` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T12:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-c0487bc97d47b3ce` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T03:02:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-d3ab27b315bd79f1` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 008", "value": 8}], "atm:effectiveEndTime": [{"evidence_text": "EFFECTIVE TIME:\n190302-191230", "val... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-d801f512c3c46d83` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_closed_status_of'}` | {'label': 'En Route TCA/Hotline web page', 'type': 'web_page'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. |
| `cand-da01d533fb6a4771` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T03:02:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:02 |
| `cand-f72ea57100cf96fd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'effective_during'}` | {'label': '19/0300 - 19/1230', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/0300 - 19/1230 |

## ATCSCC-GOLD-044 / 2026-05-16:026

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=26
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. ZAU SWAP STATEMENT: SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR THE SOUTHERN PORTION OF ZAU AIRSPACE THIS MORNING ACROSS SOUTHEASTERN ILLINOIS AND INDIANA AFTER 1200Z. EXPECTED IMPACT AREA: THUNDERSTORMS ARE EXPECTED TO IMPACT CHICAGO METRO SOUTHBOUND DEPARTURES UTILIZING THE C-D-E TRACKS. PLANNED ALTERNATE DEPARTURE ROUTES: DEPARTURES LANDING INTERNAL ZAU AIRPORTS SOUTH OF ORD/MDW MAY FILE NORMAL ROUTES BUT ARE ENCOURAGED TO FUEL FOR POSSIBLE TACTICAL REROUTES. SOUTHBOUND DE...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00ca1e4552759831` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 26, "atm:controlledNASelement": {"id": "ZAU", "type": "nas:ARTCC"}, "atm:effectiveEndTime": "2026-05-16T23:00:00Z", "atm:effectiveStar... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-0535155ec332380a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should_contact` | ZAU TMU at (630) 906-8241 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE CONTACT ZAU TMU AT (630) 906-8241 WITH ANY QUESTIONS. |
| `cand-0af4b731be6ad661` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_encouraged_to_utilize` | CDR eastbound via the 2E CDR or CDR's via BACEN in the B track | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEPARTURES TO ZID, ZTL/FLORIDA AND TOBACCO ROAD ARE ENCOURAGED TO UTILIZE CDR EASTBOUND VIA THE 2E CDR OR UTILIZE CDR'S VIA BACEN IN THE B TRACK. |
| `cand-123422dd4fa5c5dc` | `S0_rule_only` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | _FYI |
| `cand-1b7e911ef8a0441f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_event_time_window` | 16/1200 - 16/2300 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1200 - 16/2300 |
| `cand-2ea619ddcf812e04` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_cause` | possible delays and MIT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | POSSIBLE DELAYS AND MIT MAY BE ASSOCIATED WITH THIS INITIATIVE |
| `cand-3f37faded7cd42bb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_advised_to_fuel_accordingly_for` | possible CDR's, playbooks, tactical reroutes and other TMI's | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE FUEL ACCORDINGLY FOR POSSIBLE CDR'S, PLAYBOOKS, TACTICAL REROUTES AND OTHER TMI'S DUE TO AIRSPACE BEING AFFECTED BY CONVECTIVE WEATHER. |
| `cand-4d77eebc382a8da2` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 26 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI |
| `cand-53462dfda78baa32` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 26, "atm:initiativeComments": "EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY.... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-610b54812e689eed` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_being_affected_by` | convective weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE FUEL ACCORDINGLY FOR POSSIBLE CDR'S, PLAYBOOKS, TACTICAL REROUTES AND OTHER TMI'S DUE TO AIRSPACE BEING AFFECTED BY CONVECTIVE WEATHER. |
| `cand-6bd6a324a03cd35b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_encouraged_to_fuel_for` | possible tactical reroutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEPARTURES LANDING INTERNAL ZAU AIRPORTS SOUTH OF ORD/MDW MAY FILE NORMAL ROUTES BUT ARE ENCOURAGED TO FUEL FOR POSSIBLE TACTICAL REROUTES. |
| `cand-6cc33cd6ace81376` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_cause` | longer than normal departure wait times | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AND MAY CAUSE LONGER THAN NORMAL DEPARTURE WAIT TIMES. |
| `cand-6f233e4680733efd` | `S2_llm_schema_slice` | `property_bundle` | `evidence_text` | {"evidence_text": "CONSTRAINED FACILITIES: ZAU"} | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-75a68684ae792015` | `S2_llm_schema_slice` | `property_bundle` | `evidence_text` | {"evidence_text": "DEPARTURES TO ZID, ZTL/FLORIDA AND TOBACCO ROAD ARE ENCOURAGED TO UTILIZE CDR EASTBOUND VIA THE 2E CDR OR UTILIZE CDR'S VIA BACEN IN THE B... | `{"rejected_evidence": 3}` | `{"missing_evidence": 3, "unknown_fact_type": 3, "unknown_predicate": 3, "unknown_subject_class": 3}` |  |
| `cand-80f90750c9ed684b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_expected_to_impact` | Chicago Metro southbound departures utilizing the C-D-E tracks | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THUNDERSTORMS ARE EXPECTED TO IMPACT CHICAGO METRO SOUTHBOUND DEPARTURES UTILIZING THE C-D-E TRACKS. |
| `cand-96c72167934756f4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_for_planning_purpose_only` | true | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-9a6eb0fa533716eb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_encouraged_to_comply_with` | ATCSCC route advisories | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. |
| `cand-d695ff94b26e7bca` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_file` | normal routes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEPARTURES LANDING INTERNAL ZAU AIRPORTS SOUTH OF ORD/MDW MAY FILE NORMAL ROUTES |
| `cand-d98486d2a1f90d3d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_facility` | ZAU | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-e5f82ad484b85827` | `S1_llm_only` | `freeform_or_unmapped_fact` | `are_anticipated_to_be_impacted` | coded departure routes and/or swaps | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOUTHBOUND DEPARTURE ROUTES VIA C-D-E TRACKS ARE ANTICIPATED TO BE IMPACTED CAUSING CODED DEPARTURE ROUTES (CDR'S) AND/OR SWAPS. |
| `cand-ea25fc86c916dedb` | `S2_llm_schema_slice` | `property_bundle` | `evidence_text` | {"evidence_text": "ORD/MDW"} | `{"rejected_evidence": 2}` | `{"missing_evidence": 2, "unknown_fact_type": 2, "unknown_predicate": 2, "unknown_subject_class": 2}` |  |
| `cand-efc7bb4ca85ab351` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expected_location` | southeastern Illinois and Indiana | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR THE SOUTHERN PORTION OF ZAU AIRSPACE THIS MORNING ACROSS SOUTHEASTERN ILLINOIS AND INDIANA AFTER 1200Z. |
| `cand-f2eefbeac61d34d0` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 26, "atm:extensionProbability": "MEDIUM", "atm:implementationStatus": "FYI", "atm:initiativeComments": "CUSTOMERS ARE ENCOURAGED TO CO... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-ffed5a401ead138b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expects_severe_weather_avoidance_plans` | southern portion of ZAU airspace | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR THE SOUTHERN PORTION OF ZAU AIRSPACE THIS MORNING ACROSS SOUTHEASTERN ILLINOIS AND INDIANA AFTER 1200Z. |

## ATCSCC-GOLD-045 / 2026-05-20:150

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=150
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI MESSAGE: EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISHAP, DEBRIS RESPONSE AREA(S) (DRAS) WILL BE ACTIVATED BY ATC, RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. AFFECTED AREAS EXTEND FROM STARBASE, TEXAS THROUGH PIARCO FIR FROM 2230Z TO 0043Z. IN THE EVENT OF A DRA ACTIVATION AN ADVISORY WILL BE SENT OUT WITH THE RELEVANT ACTIVATED DRA, TIME OF THE ACTIVATION, AND THE EXPECTED END TIME OF DEBRIS FALL. DEBRIS FALL COULD OCCURR FOR U...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04fc8a36bbaafcaf` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-20T21:21:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 21:21 |
| `cand-05c4a9e808243008` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'instructs_flight_crews_to_be_aware_of'}` | {'label': 'possible impacts', 'type': 'operational_risk'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE FLIGHT CREWS ARE AWARE OF POSSIBLE IMPACTS |
| `cand-083eacf42dae0977` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-20T22:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-17e1a2f476018787` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_event_time_window'}` | {'label': '20/2230 - 21/2230', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-19df9507d4045023` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T21:21:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:21 |
| `cand-1d5a2d0def1a992c` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202121-212300 |
| `cand-2d9e5940d2891cc2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'may_trigger'}` | {'label': 'groundstops', 'type': 'traffic_management_initiative'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-3eba2f9ed5235ef9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'instructs_flights_to_be_fueled_accordingly'}` | {'label': 'possible impacts', 'type': 'operational_risk'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AND THAT FLIGHTS ARE FUELED ACCORDINGLY. |
| `cand-4cff1b1dd7b8e68c` | `S0_rule_only` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | _FYI |
| `cand-606083cf8b82f8a1` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISHAP, DEBRIS RESPONSE AREA(S) (... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISH... |
| `cand-60fa03f8a2ef41c4` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-67000d16e403a664` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'names_constrained_facility'}` | {'label': 'ZHU', 'type': 'air_traffic_control_facility'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZHU |
| `cand-679173f8a21023d8` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 150 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-9045012d6087d984` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-21T22:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-9cab61285ee75e43` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_update_will_announce'}` | {'label': 'involved airspace released and normal traffic resumed', 'type': 'airspace_status_update'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AN UPDATE WILL BE SENT OUT ADVISING THE INVLOVED AIRSPACE IS RELEASED AND THAT NORMAL TRAFFIC HAS RESUMED. |
| `cand-b852c2f17071d1fc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'may_trigger'}` | {'label': 'airborne holding', 'type': 'traffic_management_initiative'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-bed3f631a239789f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_tentative_launch'}` | {'label': 'SpaceX SuperHeavy Starship Flt-12 launch from Starbase, Texas on May-21-2026', 'type': 'launch_event'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. |
| `cand-cafa23aaf76a6a59` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'may_trigger'}` | {'label': 'route closures', 'type': 'traffic_management_initiative'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-d337fe15de999a23` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'could_occur_for_up_to'}` | {'label': '151 minutes', 'type': 'duration'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEBRIS FALL COULD OCCURR FOR UP TO 151 MINUTES. |
| `cand-d6bd1e8295a7c27b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | ZHU | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-dfca890d913e40db` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_affected_areas_extend_through'}` | {'label': 'Piarco FIR', 'type': 'airspace_region'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AFFECTED AREAS EXTEND FROM STARBASE, TEXAS THROUGH PIARCO FIR FROM 2230Z TO 0043Z. |
| `cand-fb0a46fa1ae3672d` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:21:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202121-212300 |
| `cand-fe8c10793178741b` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 150, "atm:effectiveEndTime": "2026-05-21T22:30:00Z", "atm:effectiveStartTime": "2026-05-20T22:30:00Z", "atm:initiativeComments": "EVEN... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |

## ATCSCC-GOLD-046 / 2026-05-18:040

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=40
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 15

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY MESSAGE: FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA SOURCE ELEV: 9456 FT AMSL ADVISORY NR: 2026/006 EFFECTIVE TIME: 180000-180000 SIGNATURE: 26/05/18 12:08 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1daea0ba9d17301e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_message_line` | FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSU... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA SOURCE ELEV: 9456 FT AMSL ADVISORY NR: 2026/006 |
| `cand-29c0ec5a9b28674f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_position` | N5559 E16035 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5559 E16035 |
| `cand-57da1b5bfcf0b338` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_signature_time` | 26/05/18 12:08 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 12:08 |
| `cand-59fcab9d059f60d4` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY", "value": 40}], "atm:initiativeComments":... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-5dfea04f7507f279` | `S2_llm_schema_slice` | `property_bundle` | `controlledNASelement` | {"atm:controlledNASelement": [{"evidence_text": "VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA", "value": "BEZYMIANNY"}]} | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-60599770de15e28c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time_window` | 180000-180000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180000-180000 |
| `cand-6cc5687c8359ba11` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_number` | 2026/006 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/006 |
| `cand-76f05d1536bb5e7a` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 40 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-9dfd3acf294a7fda` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-a90853cb5828c1e4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `issues_volcano_advisory_for` | BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: ANCHORAGE VOLCANO: BEZYMIANNY |
| `cand-b3e3c771b268d996` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_header` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-b4f0614016dceae3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_source_elevation` | 9456 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 9456 FT AMSL |
| `cand-d32838e7ec233568` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T12:00:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 12:08 |
| `cand-e9c12e516ea379c8` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-f51229c4192b7e36` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_located_in_area` | KAMCHATKA PENINSULA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA PENINSULA |

## ATCSCC-GOLD-047 / 2026-05-14:033

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=33
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 18

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE MESSAGE: FVXX24 KNES 141100 WSI DDS:141102 VA ADVISORY DTG: 20260514/1100Z VAAC: WASHINGTON VOLCANO: PURACE 351060 PSN: N0219 W07624 AREA: COLOMBIA SOURCE ELEV: 15256 FT AMSL ADVISORY NR: 2026/071 INFO SOURCE: GOES-19. VONA. NWP MODELS. ERUPTION DETAILS: VA EM DETECTED EST VA DTG: 14/1030Z EST VA CLD: SFC/FL170 N0232 W07632 - N0220 W07623 - N0217 W07624 - N0225 W07640 - N0232 W07632 MOV NW 5KT FCST VA CLD +6HR: 14/1630Z SFC/FL170 N0241 W07637 - N0220 W07623 - N0217 W07624 - N0230 W07648 - N0241 W07637 FCST VA CLD +12HR: 14/2230Z SFC/FL170 N0238 W07641 - N0220 W07623 - N0217 W07624 - N0225 W07650 - N0238 W07641 FCST VA CLD +18HR: 15/0430Z S...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b0c080c737e786b` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 33 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-0e52ff716e0dd088` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_ash_emission_moving_from'}` | {'label': 'summit', 'type': 'location'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VONA RCVD FOR VA EM MOVNG NW FM SUMMIT. |
| `cand-37e19024a28b1639` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_position_at_plus_6_hours'}` | {'label': 'N0241 W07637', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/1630Z SFC/FL170 N0241 W07637 - N0220 W07623 - N0217 W07624 - N0230 W07648 - N0241 W07637 |
| `cand-41f85504f3d813a9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'expected_movement_through'}` | {'label': 'T+18 HRS', 'type': 'time_span'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXP WNW MOVNT THRU T+18 HRS. |
| `cand-4c8635e6d5a0381e` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-4cbd2312fb3b4e58` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_position'}` | {'label': 'N0219 W07624', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: PURACE 351060 PSN: N0219 W07624 |
| `cand-59b43ac0820cef10` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_position_at_plus_18_hours'}` | {'label': 'N0232 W07646', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/0430Z SFC/FL170 N0232 W07646 - N0220 W07623 - N0217 W07623 - N0217 W07651 - N0232 W07646 |
| `cand-5bf41ccb22120839` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_observed_vertical_extent'}` | {'label': 'SFC/FL170', 'type': 'flight_level_range'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL170 |
| `cand-6186a9f3bcb6138e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_volcano'}` | {'label': 'Purace', 'type': 'volcano'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-7f5ef48c167b7be7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_position_at_plus_12_hours'}` | {'label': 'N0238 W07641', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/2230Z SFC/FL170 N0238 W07641 - N0220 W07623 - N0217 W07624 - N0225 W07650 - N0238 W07641 |
| `cand-a514ef96b8169d06` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'was_not_seen_in'}` | {'label': 'satellite image', 'type': 'imagery'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT SEEN IN STLT IMG DUE TO MET CLD CVR IN SUMMIT AREA. |
| `cand-a7dcec86c28fd123` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-c1e384754b06fda7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_source_elevation'}` | {'label': '15256 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 15256 FT AMSL |
| `cand-c242b9ea21c50432` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T11:00:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 11:02 |
| `cand-c8ea318119602977` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is_in_area'}` | {'label': 'Colombia', 'type': 'country'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: COLOMBIA |
| `cand-ddd5119bb3c2967e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_advisory_number'}` | {'label': '2026/071', 'type': 'advisory_number'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/071 |
| `cand-e179cfef2cf17a31` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is_moving'}` | {'label': 'NW 5KT', 'type': 'movement'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 5KT |
| `cand-ece999aff28f83e8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'was_detected_at'}` | {'label': '14/1030Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EM DETECTED EST VA DTG: 14/1030Z |

## ATCSCC-GOLD-048 / 2026-05-17:003

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=3
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 12

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-171200 SIGNATURE: 26/05/17 00:43 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0170faf244194b82` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 3, "atm:effectiveEndTime": "2026-05-17T12:00:00Z", "atm:effectiveStartTime": "2026-05-17T00:43:00Z", "atm:initiativeComments": "THE TE... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-17120... |
| `cand-08138ecf1101f27b` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 3 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION |
| `cand-0d8b9fa4dea4b96e` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-217db584d98a952c` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170043-171200 |
| `cand-22603fb711c1a837` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'instruction'}` | {'label': 'normal ATCSCC phone lines', 'type': 'contact method'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-413dd235a94b1345` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'state'}` | {'label': 'closed', 'type': 'status'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. |
| `cand-6f22109771e33824` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170043-171200 |
| `cand-8946c9e83c4e90b7` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-9c1dcc4dbf62eace` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'time interval'}` | {'label': '170043-171200', 'type': 'time interval'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-ab7a06497b76b3d1` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T00:43:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 00:43 |
| `cand-c19457bef5143a19` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-d78b70a7c7530e83` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 3 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION |

## ATCSCC-GOLD-049 / 2026-05-19:013

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=13
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 20

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL MESSAGE: FVXX24 KNES 190606 WSI DDS:190609 VA ADVISORY DTG: 20260519/0606Z VAAC: WASHINGTON VOLCANO: POPOCATEPETL 341090 PSN: N1901 W09837 AREA: MEXICO SOURCE ELEV: 17693 FT AMSL ADVISORY NR: 2026/196 INFO SOURCE: GOES-19. WEBCAM. ERUPTION DETAILS: VA EMS ENDED OBS VA DTG: 19/0551Z OBS VA CLD: VA NOT IDENTIFIABLE FM STLT DATA FCST VA CLD +6HR: 19/1200Z NO VA EXP FCST VA CLD +12HR: 19/1800Z NO VA EXP FCST VA CLD +18HR: 20/0000Z NO VA EXP RMK: VA NOT DETECTED ON VARIOUS STLT PRODUCTS. WEBCAM SHOWS ONLY STEAM/GAS EMS CURRENTLY. NEW VA EMS LIKELY AT ANY TIME. ...KONON EFFECTIVE TIME: 190000-190000 SIGNATURE: 26/05/19 06:09 FAA.gov Home \|...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0d45bb903843dc03` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reported_source_elevation'}` | {'class': 'Elevation', 'name': '17693 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 17693 FT AMSL |
| `cand-108d2f7f17640892` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 13 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-206f4e03bdaf4eb0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'ended_at_observation_time'}` | {'class': 'Observation Time', 'name': '19/0551Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS ENDED OBS VA DTG: 19/0551Z |
| `cand-25ca52761cbdcde7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_volcano'}` | {'class': 'Volcano', 'name': 'POPOCATEPETL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-3ad89bc89043ef84` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '20/0000Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/0000Z NO VA EXP |
| `cand-3e3b6058f482b52e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'warns_new_ash_emission_possible_any_time'}` | {'class': 'Probability statement', 'name': 'NEW VA EMS LIKELY AT ANY TIME'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW VA EMS LIKELY AT ANY TIME. |
| `cand-6ce23877abf8d8f2` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T06:06:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 06:09 |
| `cand-6d114306422a094e` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-74acbe5f4e208deb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_steam_gas_only_currently'}` | {'class': 'Emission type', 'name': 'STEAM/GAS EMS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WEBCAM SHOWS ONLY STEAM/GAS EMS CURRENTLY. |
| `cand-8b9e2b3f00bc81ac` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-a200101c9863c33c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'not_identifiable_from_satellite_data'}` | {'class': 'Observation result', 'name': 'VA NOT IDENTIFIABLE FM STLT DATA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: VA NOT IDENTIFIABLE FM STLT DATA |
| `cand-a8a16fefdc34e6c9` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 13 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-b21f651044824e18` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '19/1800Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/1800Z NO VA EXP |
| `cand-c139b59871133e01` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'located_in_area'}` | {'class': 'Geographic Area', 'name': 'MEXICO'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: MEXICO |
| `cand-cf8f948d0fa26f00` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'indicates_not_detected_on_satellite_products'}` | {'class': 'Observation summary', 'name': 'VA NOT DETECTED ON VARIOUS STLT PRODUCTS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: VA NOT DETECTED ON VARIOUS STLT PRODUCTS. |
| `cand-db13defb0c82d7f1` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-e00fbf3b6ae4d058` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-e3754640e23f658e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '19/1200Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/1200Z NO VA EXP |
| `cand-e4ee7d03590baa70` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-19T06:09:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 06:09 |
| `cand-f84d3921e54211fe` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |

## ATCSCC-GOLD-050 / 2026-05-19:043

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=43
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 191422 WSI DDS:191425 VA ADVISORY DTG: 20260519/1422Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/582 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: FRQT VA EMS OBS VA DTG: 19/1350Z OBS VA CLD: SFC/FL150 N1429 W09052 - N1427 W09053 - N1415 W09158 - N1429 W09209 - N1429 W09052 MOV SW 15KT FCST VA CLD +6HR: 19/2000Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1402 W09156 - N1416 W09208 - N1429 W09053 FCST VA CLD +12HR: 20/0200Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1404 W09158 - N1420 W09208 - N1429 W09053 FCST VA CLD +18HR: 20/0800Z SF...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-067e03b0b568351e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_source_elevation` | 12346 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-0690c573c41cdfe5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_title` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-0fed7780f4b6d471` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed_movement_direction` | SW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 15KT |
| `cand-24ce0b81fea6711b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `based_on` | WEBCAM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-3939e709a889dab5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_volcano_identifier` | 342090 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 |
| `cand-4538e2c61e42b166` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observation_time` | 19/1350Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 19/1350Z |
| `cand-45e10043ad4be2a4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_date_time` | 20260519/1422Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260519/1422Z |
| `cand-4af0c9e9afac4e2e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `based_on` | STLT OBS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-4e37c4012cdedc81` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-19T14:25:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:25 |
| `cand-5f722d1909779125` | `S1_llm_only` | `freeform_or_unmapped_fact` | `based_on` | NWP MDLS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-6ceb731937bda75f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed_flight_level_range` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 |
| `cand-7ac2eec0c2a38a0f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed_in` | WEBCAM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBSD IN WEBCAM |
| `cand-7d87057290514fdd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed_in` | STLT IMG | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBSD IN WEBCAM AND STLT IMG |
| `cand-7fa5341b78ac87b5` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-8e93feeb760222f0` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 43 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-935e2f841e7d5561` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T14:22:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 14:25 |
| `cand-99743623fd36bcf8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_number` | 2026/582 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/582 |
| `cand-b58bf7485aa65ce4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_reported_by` | WASHINGTON VAAC | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: WASHINGTON |
| `cand-c5ef223c26350c7b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expected_shift_by_time_horizon` | shift SW by T+18 HRS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WSW MVMT EXP TO SHIFT SW BY T+18 HRS |
| `cand-cff3680c3d92d529` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-d684b38c09801a4a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_located_in_area` | GUATEMALA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: GUATEMALA |
| `cand-db0a5aa5217249a6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed_movement_speed` | 15KT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 15KT |
| `cand-db6c88d073002906` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-de7615779fe65b41` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-e1c9e9e216a04e70` | `S1_llm_only` | `freeform_or_unmapped_fact` | `eruption_activity_description` | FRQT VA EMS OBS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: FRQT VA EMS OBS |
| `cand-e243e74fafb2416d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `estimated_extent_from_summit` | approx 70 NM WSW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXTG APPRX 70 NM WSW FM SUMMIT |
| `cand-e8a8cbeaf112251c` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-fa1b8ebb4188190d` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 43 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
