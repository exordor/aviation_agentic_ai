# NASA ATMONTO Gold Review batch_05

- Samples: `ATCSCC-GOLD-041` to `ATCSCC-GOLD-050`
- Records: 10
- Candidate clusters: 243

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-041 / 2026-05-18:054

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=54
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. EFFECTIVE TIME: 181357-181630 SIGNATURE: 26/05/18 13:57 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0287280efd166879` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | SIGNATURE: 26/05/18 13:57 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 13:57 |
| `cand-0d7f20c246594bb1` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-1045c190186daf1d` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-17318a6a0c6a8ef0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T13:57:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181357-181630 |
| `cand-1da2aa2b2d1a7caa` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-2002b3c636436b34` | `S1_llm_only` | `canonical_fact` | `'should_file'}` | {'label': 'alternate routing', 'type': 'routing_action'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-2cfeb9fe98b30060` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 54 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-32d57d45dd7a83ca` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T13:57:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-36132ba27682f08d` | `S1_llm_only` | `canonical_fact` | `'removes'}` | {'label': 'L455', 'type': 'route'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *REMOVES L455* |
| `cand-456f37f194722a42` | `S1_llm_only` | `canonical_fact` | `'is_closed_due_to'}` | {'label': 'thunderstorms', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-4cf1162854bcfe9c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T16:30:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-5c45f237fb294308` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T16:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181357-181630 |
| `cand-5caeab04cd6aef4c` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-92274698b0dbed3c` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T13:57:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-9229b9ee1c03099a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | CONSTRAINED FACILITIES: ZNY | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-9b2ca28d9b1e64a3` | `S1_llm_only` | `canonical_fact` | `'replaces'}` | {'label': 'advisory 035', 'type': 'advisory'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES ADVZY 035*** |
| `cand-a7ae44b32c339560` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-a8ca574b029dd68f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | EVENT TIME: 18/1130 - 18/1600 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1130 - 18/1600 |
| `cand-b0d0a176accf52ca` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-b5f37bebb9882144` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | OCEANIC ROUTE CLOSURE_RQD | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-bdc0022818fce3cb` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | USERS SHOULD FILE ALTERNATE ROUTING. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-ce83d0fb832a910c` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-d1545d44d0f09055` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 54 | `{"repaired_accepted": 1}` | `{}` | ***REPLACES ADVZY 035*** |
| `cand-e01da3ff59c89ba3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS... | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-e45ab184a633715f` | `S1_llm_only` | `canonical_fact` | `'constrains_facility'}` | {'label': 'ZNY', 'type': 'facility'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-f43b03e61ed3f6cc` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T13:57:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 13:57 |
| `cand-feed894093738348` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 54 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |

## ATCSCC-GOLD-042 / 2026-05-20:015

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=15
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. EFFECTIVE TIME: 200051-200330 SIGNATURE: 26/05/20 00:51 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-016190caeff7aea2` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-039363b9ebc64800` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-26bec8b9dde1754f` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMA |
| `cand-2d32195c080d1450` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-36195c5046792989` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:51:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200051-200330 |
| `cand-4672720305d9c15e` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 15 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-4a3cde007ab37f78` | `S1_llm_only` | `canonical_fact` | `states_effective_time` | 200051-200330 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200051-200330 |
| `cand-4f9253bf7c1f0e58` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-5dcaf79b634f7855` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 15 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-620ac2fcdb222f29` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteType` | ROUTE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-68a8dee020aa8665` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-6c1cc25fe8b0a1b2` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T00:51:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-88fe62fbf29655c9` | `S1_llm_only` | `canonical_fact` | `replaces_advisory` | 136 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *REPLACES ADVISORY 136 |
| `cand-944e6de2e1b804fd` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZMA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-978d1008f2d343b8` | `S1_llm_only` | `canonical_fact` | `has_advisory_identifier_text` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-a33265f6f335284c` | `S1_llm_only` | `canonical_fact` | `extends_time_for_route` | L451 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | **EXTENDS TIME FOR L451 |
| `cand-a3f27863bc67c9db` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T03:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200051-200330 |
| `cand-b20296e7c9e04e84` | `S1_llm_only` | `canonical_fact` | `are_encouraged_to_file` | alternate routes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. |
| `cand-bd188c397a587ab3` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-c58104ff8a8859b2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T00:51:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:51 |
| `cand-e368c03d5a2c92cc` | `S1_llm_only` | `canonical_fact` | `advises_route_status` | L451 is closed due to thunderstorms | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-ea1fa272914e47c1` | `S1_llm_only` | `canonical_fact` | `states_event_time` | 19/2200 - 20/0300Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/2200 - 20/0300Z |
| `cand-f166154bb65686f7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | ZMA | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |
| `cand-f9267fa950ffd9a1` | `S1_llm_only` | `canonical_fact` | `has_constrained_facility` | ZMA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA |
| `cand-fb5fa533102b6fed` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteReason` | WEATHER | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUND... |

## ATCSCC-GOLD-043 / 2026-05-19:008

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=8
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 190302-191230 SIGNATURE: 26/05/19 03:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-23706449ac1fe50a` | `S1_llm_only` | `canonical_fact` | `'shows_effective_time_as'}` | {'label': '190302-191230', 'type': 'effective_time_string'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190302-191230 |
| `cand-265edd8e487f21d8` | `S1_llm_only` | `canonical_fact` | `'announces_closed_status_of'}` | {'label': 'En Route TCA/Hotline web page', 'type': 'web_page'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. |
| `cand-300f17961807e6f6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-19T03:02:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:02 |
| `cand-3a9d350c079bc73c` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| `cand-4407f5878b82ef94` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T03:00:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER AS... |
| `cand-52545e96d1e08501` | `S1_llm_only` | `canonical_fact` | `'instructs_use_of'}` | {'label': 'normal ATCSCC phone lines', 'type': 'phone_lines'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-59cdcaf48011f245` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T12:30:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER AS... |
| `cand-734b48c0bed1f4e9` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER AS... |
| `cand-7ba39ef03c0204b1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 8 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| `cand-817ca64004d62151` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 8 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER AS... |
| `cand-8367d05047ac5fb5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T03:02:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-aeb02f27ae9d6ac6` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-b5faf793471d1066` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 8 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 |
| `cand-bc174b0c0114647e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T12:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-c0487bc97d47b3ce` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T03:02:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-c3502b79432ae522` | `S1_llm_only` | `canonical_fact` | `'effective_during'}` | {'label': '19/0300 - 19/1230', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/0300 - 19/1230 |
| `cand-c70813cd7fd7957e` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T12:30:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-ccc2d727f07aa495` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T03:02:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER AS... |
| `cand-da01d533fb6a4771` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T03:02:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:02 |

## ATCSCC-GOLD-044 / 2026-05-16:026

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=26
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 43

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. ZAU SWAP STATEMENT: SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR THE SOUTHERN PORTION OF ZAU AIRSPACE THIS MORNING ACROSS SOUTHEASTERN ILLINOIS AND INDIANA AFTER 1200Z. EXPECTED IMPACT AREA: THUNDERSTORMS ARE EXPECTED TO IMPACT CHICAGO METRO SOUTHBOUND DEPARTURES UTILIZING THE C-D-E TRACKS. PLANNED ALTERNATE DEPARTURE ROUTES: DEPARTURES LANDING INTERNAL ZAU AIRPORTS SOUTH OF ORD/MDW MAY FILE NORMAL ROUTES BUT ARE ENCOURAGED TO FUEL FOR POSSIBLE TACTICAL REROUTES. SOUTHBOUND DE...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0138893af61bd1c4` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 26 | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-04a135496106cdd9` | `S1_llm_only` | `canonical_fact` | `expects_severe_weather_avoidance_plans` | southern portion of ZAU airspace | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR THE SOUTHERN PORTION OF ZAU AIRSPACE THIS MORNING ACROSS SOUTHEASTERN ILLINOIS AND INDIANA AFTER 1200Z. |
| `cand-06e2f78c607e9167` | `S1_llm_only` | `canonical_fact` | `should_contact` | ZAU TMU at (630) 906-8241 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE CONTACT ZAU TMU AT (630) 906-8241 WITH ANY QUESTIONS. |
| `cand-0b7b31fbb75c9ded` | `S1_llm_only` | `canonical_fact` | `expected_location` | southeastern Illinois and Indiana | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR THE SOUTHERN PORTION OF ZAU AIRSPACE THIS MORNING ACROSS SOUTHEASTERN ILLINOIS AND INDIANA AFTER 1200Z. |
| `cand-11285f3f415ac5f3` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-123422dd4fa5c5dc` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | FYI | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _FYI |
| `cand-16e0bf426e8c14c9` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROU... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-21fad5e03248cc05` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-23bc940d63587b2b` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-3624f5ade6d0ea3b` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 26 | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-37f3b15a92d45c97` | `S1_llm_only` | `canonical_fact` | `are_encouraged_to_utilize` | CDR eastbound via the 2E CDR or CDR's via BACEN in the B track | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEPARTURES TO ZID, ZTL/FLORIDA AND TOBACCO ROAD ARE ENCOURAGED TO UTILIZE CDR EASTBOUND VIA THE 2E CDR OR UTILIZE CDR'S VIA BACEN IN THE B TRACK. |
| `cand-3877a339a2d75b9a` | `S1_llm_only` | `canonical_fact` | `are_anticipated_to_be_impacted` | coded departure routes and/or swaps | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOUTHBOUND DEPARTURE ROUTES VIA C-D-E TRACKS ARE ANTICIPATED TO BE IMPACTED CAUSING CODED DEPARTURE ROUTES (CDR'S) AND/OR SWAPS. |
| `cand-3f13f86aa193a270` | `S1_llm_only` | `canonical_fact` | `may_cause` | longer than normal departure wait times | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AND MAY CAUSE LONGER THAN NORMAL DEPARTURE WAIT TIMES. |
| `cand-46187fa345c67b3a` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-46cd7f2bef4e06c6` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | CDR | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-4d77eebc382a8da2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 26 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI |
| `cand-645174336b275ca7` | `S1_llm_only` | `canonical_fact` | `are_expected_to_impact` | Chicago Metro southbound departures utilizing the C-D-E tracks | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THUNDERSTORMS ARE EXPECTED TO IMPACT CHICAGO METRO SOUTHBOUND DEPARTURES UTILIZING THE C-D-E TRACKS. |
| `cand-6f233e4680733efd` | `S2_llm_schema_slice` | `property_bundle` | `evidence_text` | {"evidence_text": "CONSTRAINED FACILITIES: ZAU"} | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1}` |  |
| `cand-72cddc125175a554` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-16T11:42:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-74b21567c5cba511` | `S1_llm_only` | `canonical_fact` | `is_being_affected_by` | convective weather | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE FUEL ACCORDINGLY FOR POSSIBLE CDR'S, PLAYBOOKS, TACTICAL REROUTES AND OTHER TMI'S DUE TO AIRSPACE BEING AFFECTED BY CONVECTIVE WEATHER. |
| `cand-75a68684ae792015` | `S2_llm_schema_slice` | `property_bundle` | `evidence_text` | {"evidence_text": "DEPARTURES TO ZID, ZTL/FLORIDA AND TOBACCO ROAD ARE ENCOURAGED TO UTILIZE CDR EASTBOUND VIA THE 2E CDR OR UTILIZE CDR'S VIA BACEN IN THE B... | `{"rejected_evidence": 3}` | `{"missing_evidence": 3, "unknown_fact_type": 3, "unknown_predicate": 3}` |  |
| `cand-7d79e65251eb8e82` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-7e7ba17ce75e7df0` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-82146662e3f0da1b` | `S1_llm_only` | `canonical_fact` | `has_event_time_window` | 16/1200 - 16/2300 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1200 - 16/2300 |
| `cand-9404d8faccb721a1` | `S1_llm_only` | `canonical_fact` | `has_constrained_facility` | ZAU | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-9aab707e7c29e982` | `S1_llm_only` | `canonical_fact` | `may_cause` | possible delays and MIT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | POSSIBLE DELAYS AND MIT MAY BE ASSOCIATED WITH THIS INITIATIVE |
| `cand-9dddf42fb0e76efb` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteType` | CDR | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-acefbe834c93adc4` | `S1_llm_only` | `canonical_fact` | `are_encouraged_to_comply_with` | ATCSCC route advisories | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. |
| `cand-ba3a40b9b2822acf` | `S1_llm_only` | `canonical_fact` | `are_encouraged_to_fuel_for` | possible tactical reroutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEPARTURES LANDING INTERNAL ZAU AIRPORTS SOUTH OF ORD/MDW MAY FILE NORMAL ROUTES BUT ARE ENCOURAGED TO FUEL FOR POSSIBLE TACTICAL REROUTES. |
| `cand-bb91be08aa8496fc` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 26 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-c1e1a778cb9754e9` | `S1_llm_only` | `canonical_fact` | `is_for_planning_purpose_only` | true | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-c68935fe164a4c85` | `S1_llm_only` | `canonical_fact` | `are_advised_to_fuel_accordingly_for` | possible CDR's, playbooks, tactical reroutes and other TMI's | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE FUEL ACCORDINGLY FOR POSSIBLE CDR'S, PLAYBOOKS, TACTICAL REROUTES AND OTHER TMI'S DUE TO AIRSPACE BEING AFFECTED BY CONVECTIVE WEATHER. |
| `cand-c8a896b98a6936cd` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | longer than normal departure wait times | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | AND MAY CAUSE LONGER THAN NORMAL DEPARTURE WAIT TIMES. |
| `cand-c99560e735b834bb` | `S1_llm_only` | `canonical_fact` | `may_file` | normal routes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEPARTURES LANDING INTERNAL ZAU AIRPORTS SOUTH OF ORD/MDW MAY FILE NORMAL ROUTES |
| `cand-d085d6077594604e` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T11:42:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-da421e3abab9acce` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T11:42:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-e3ca1c5447e8c0c6` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | possible delays and mit | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | POSSIBLE DELAYS AND MIT MAY BE ASSOCIATED WITH THIS INITIATIVE |
| `cand-e6e9344b185edc93` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-ea25fc86c916dedb` | `S2_llm_schema_slice` | `property_bundle` | `evidence_text` | {"evidence_text": "ORD/MDW"} | `{"rejected_evidence": 2}` | `{"missing_evidence": 2, "unknown_fact_type": 2, "unknown_predicate": 2}` |  |
| `cand-ef6adbd30b66e293` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZAU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |
| `cand-f35e9ca9c02bfda3` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. ZAU SWAP STATEMENT: SEVERE WEATHER AVOIDANCE PLANS ARE EXPECTED FOR THE SOUTHERN PORTION... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-f826f327f3de19a4` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-fe0b57fd9dd61ebe` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T12:00:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI RAW TEXT: EVENT TIME: 16/1200 - 16/2300 CONSTRAINED FACILITIES: ZAU THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUT... |

## ATCSCC-GOLD-045 / 2026-05-20:150

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=150
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI MESSAGE: EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISHAP, DEBRIS RESPONSE AREA(S) (DRAS) WILL BE ACTIVATED BY ATC, RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. AFFECTED AREAS EXTEND FROM STARBASE, TEXAS THROUGH PIARCO FIR FROM 2230Z TO 0043Z. IN THE EVENT OF A DRA ACTIVATION AN ADVISORY WILL BE SENT OUT WITH THE RELEVANT ACTIVATED DRA, TIME OF THE ACTIVATION, AND THE EXPECTED END TIME OF DEBRIS FALL. DEBRIS FALL COULD OCCURR FOR U...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02e3ceacfb876d0f` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZHU |
| `cand-19df9507d4045023` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T21:21:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:21 |
| `cand-1d5a2d0def1a992c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T23:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202121-212300 |
| `cand-2115441a6c3baad0` | `S1_llm_only` | `canonical_fact` | `'has_affected_areas_extend_through'}` | {'label': 'Piarco FIR', 'type': 'airspace_region'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AFFECTED AREAS EXTEND FROM STARBASE, TEXAS THROUGH PIARCO FIR FROM 2230Z TO 0043Z. |
| `cand-25a51ef5f5aaab5a` | `S1_llm_only` | `canonical_fact` | `'could_occur_for_up_to'}` | {'label': '151 minutes', 'type': 'duration'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEBRIS FALL COULD OCCURR FOR UP TO 151 MINUTES. |
| `cand-295ab5086f96772b` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T22:30:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-33cfb0cd27e41765` | `S1_llm_only` | `canonical_fact` | `'announces_tentative_launch'}` | {'label': 'SpaceX SuperHeavy Starship Flt-12 launch from Starbase, Texas on May-21-2026', 'type': 'launch_event'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. |
| `cand-45ae3789e7f59ce6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T22:30:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-497d040812270aae` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 150 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-4cff1b1dd7b8e68c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | FYI | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _FYI |
| `cand-58c59c0307045382` | `S1_llm_only` | `canonical_fact` | `'instructs_flight_crews_to_be_aware_of'}` | {'label': 'possible impacts', 'type': 'operational_risk'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE FLIGHT CREWS ARE AWARE OF POSSIBLE IMPACTS |
| `cand-604258463f1eb0c3` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T22:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-636104dd690cea73` | `S1_llm_only` | `canonical_fact` | `'names_constrained_facility'}` | {'label': 'ZHU', 'type': 'air_traffic_control_facility'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZHU |
| `cand-679173f8a21023d8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 150 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-68071f9cb7cd520f` | `S1_llm_only` | `canonical_fact` | `'has_event_time_window'}` | {'label': '20/2230 - 21/2230', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-7657e5fc7a3e96a5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-20T21:21:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-7f458e4c84e2e3a2` | `S1_llm_only` | `canonical_fact` | `'states_update_will_announce'}` | {'label': 'involved airspace released and normal traffic resumed', 'type': 'airspace_status_update'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AN UPDATE WILL BE SENT OUT ADVISING THE INVLOVED AIRSPACE IS RELEASED AND THAT NORMAL TRAFFIC HAS RESUMED. |
| `cand-90ffe61805bda1e8` | `S1_llm_only` | `canonical_fact` | `'may_trigger'}` | {'label': 'airborne holding', 'type': 'traffic_management_initiative'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-9fc5e114379bf7e3` | `S1_llm_only` | `canonical_fact` | `'may_trigger'}` | {'label': 'groundstops', 'type': 'traffic_management_initiative'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-abe7a739057f2d0b` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T22:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-aef8512994086b0f` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISHAP, DEBRIS RESPONSE AREA(S) (... | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISH... |
| `cand-d4801c84bfd41942` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 150 | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-d4b39d5aa20c6636` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T21:21:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 21:21 |
| `cand-d5d3a9629f93f62b` | `S1_llm_only` | `canonical_fact` | `'may_trigger'}` | {'label': 'route closures', 'type': 'traffic_management_initiative'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-da0f6018bbb1fc3f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STA... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-ecdcabf170a80ac0` | `S1_llm_only` | `canonical_fact` | `'instructs_flights_to_be_fueled_accordingly'}` | {'label': 'possible impacts', 'type': 'operational_risk'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AND THAT FLIGHTS ARE FUELED ACCORDINGLY. |
| `cand-f9df334fc8565a3c` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZHU | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-fb0a46fa1ae3672d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:21:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202121-212300 |

## ATCSCC-GOLD-046 / 2026-05-18:040

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=40
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY MESSAGE: FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA SOURCE ELEV: 9456 FT AMSL ADVISORY NR: 2026/006 EFFECTIVE TIME: 180000-180000 SIGNATURE: 26/05/18 12:08 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b8c7952de0151e7` | `S1_llm_only` | `canonical_fact` | `has_position` | N5559 E16035 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5559 E16035 |
| `cand-37af7000f1f8116c` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | BEZYMIANNY | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA |
| `cand-470197c39e38168f` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T12:08:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 12:08 |
| `cand-4eddadf624bd3f4f` | `S1_llm_only` | `canonical_fact` | `is_located_in_area` | KAMCHATKA PENINSULA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA PENINSULA |
| `cand-608762802b7c6601` | `S1_llm_only` | `canonical_fact` | `has_advisory_number` | 2026/006 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/006 |
| `cand-61b74d1d30bf3b09` | `S1_llm_only` | `canonical_fact` | `reports_message_line` | FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSU... | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA SOURCE ELEV: 9456 FT AMSL ADVISORY NR: 2026/006 |
| `cand-76f05d1536bb5e7a` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 40 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-8cd64d90a7e0b0f5` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 40 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/006 |
| `cand-9dfd3acf294a7fda` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-a7dac989893edcd6` | `S1_llm_only` | `canonical_fact` | `issues_volcano_advisory_for` | BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: ANCHORAGE VOLCANO: BEZYMIANNY |
| `cand-ac9a1f2574cd8e96` | `S1_llm_only` | `canonical_fact` | `has_signature_time` | 26/05/18 12:08 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 12:08 |
| `cand-b2e8266bc3c94c52` | `S1_llm_only` | `canonical_fact` | `has_advisory_header` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-c33d611130929f07` | `S1_llm_only` | `canonical_fact` | `has_effective_time_window` | 180000-180000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180000-180000 |
| `cand-c834809086527b3f` | `S1_llm_only` | `canonical_fact` | `has_source_elevation` | 9456 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 9456 FT AMSL |
| `cand-d32838e7ec233568` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T12:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 12:08 |
| `cand-e9c12e516ea379c8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-efc857af97803b48` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |

## ATCSCC-GOLD-047 / 2026-05-14:033

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=33
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE MESSAGE: FVXX24 KNES 141100 WSI DDS:141102 VA ADVISORY DTG: 20260514/1100Z VAAC: WASHINGTON VOLCANO: PURACE 351060 PSN: N0219 W07624 AREA: COLOMBIA SOURCE ELEV: 15256 FT AMSL ADVISORY NR: 2026/071 INFO SOURCE: GOES-19. VONA. NWP MODELS. ERUPTION DETAILS: VA EM DETECTED EST VA DTG: 14/1030Z EST VA CLD: SFC/FL170 N0232 W07632 - N0220 W07623 - N0217 W07624 - N0225 W07640 - N0232 W07632 MOV NW 5KT FCST VA CLD +6HR: 14/1630Z SFC/FL170 N0241 W07637 - N0220 W07623 - N0217 W07624 - N0230 W07648 - N0241 W07637 FCST VA CLD +12HR: 14/2230Z SFC/FL170 N0238 W07641 - N0220 W07623 - N0217 W07624 - N0225 W07650 - N0238 W07641 FCST VA CLD +18HR: 15/0430Z S...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b0c080c737e786b` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 33 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-2f56d41a1e0c90e8` | `S1_llm_only` | `canonical_fact` | `'has_position'}` | {'label': 'N0219 W07624', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: PURACE 351060 PSN: N0219 W07624 |
| `cand-3b80494d541413f6` | `S1_llm_only` | `canonical_fact` | `'was_not_seen_in'}` | {'label': 'satellite image', 'type': 'imagery'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT SEEN IN STLT IMG DUE TO MET CLD CVR IN SUMMIT AREA. |
| `cand-3da92497c88e24c6` | `S1_llm_only` | `canonical_fact` | `'reports_ash_emission_moving_from'}` | {'label': 'summit', 'type': 'location'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VONA RCVD FOR VA EM MOVNG NW FM SUMMIT. |
| `cand-4c8635e6d5a0381e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-5b3201ba096aa883` | `S1_llm_only` | `canonical_fact` | `'is_moving'}` | {'label': 'NW 5KT', 'type': 'movement'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 5KT |
| `cand-916b5d1bf8be0f23` | `S1_llm_only` | `canonical_fact` | `'forecast_position_at_plus_12_hours'}` | {'label': 'N0238 W07641', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/2230Z SFC/FL170 N0238 W07641 - N0220 W07623 - N0217 W07624 - N0225 W07650 - N0238 W07641 |
| `cand-98b134aae249d283` | `S1_llm_only` | `canonical_fact` | `'is_in_area'}` | {'label': 'Colombia', 'type': 'country'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: COLOMBIA |
| `cand-a0cd9745a7cbd019` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 33 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/071 |
| `cand-a7dcec86c28fd123` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-b1fa442bdccc50c1` | `S1_llm_only` | `canonical_fact` | `'forecast_position_at_plus_18_hours'}` | {'label': 'N0232 W07646', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/0430Z SFC/FL170 N0232 W07646 - N0220 W07623 - N0217 W07623 - N0217 W07651 - N0232 W07646 |
| `cand-b82c58ef708eaaa2` | `S1_llm_only` | `canonical_fact` | `'forecast_position_at_plus_6_hours'}` | {'label': 'N0241 W07637', 'type': 'coordinates'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/1630Z SFC/FL170 N0241 W07637 - N0220 W07623 - N0217 W07624 - N0230 W07648 - N0241 W07637 |
| `cand-c242b9ea21c50432` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-14T11:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 11:02 |
| `cand-c2be2857c37a72a6` | `S1_llm_only` | `canonical_fact` | `'reports_advisory_number'}` | {'label': '2026/071', 'type': 'advisory_number'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/071 |
| `cand-d2f257c54c466e57` | `S1_llm_only` | `canonical_fact` | `'expected_movement_through'}` | {'label': 'T+18 HRS', 'type': 'time_span'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXP WNW MOVNT THRU T+18 HRS. |
| `cand-e3e6c1586bceb23e` | `S1_llm_only` | `canonical_fact` | `'identifies_volcano'}` | {'label': 'Purace', 'type': 'volcano'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-e4cb4d9ad54ee7ce` | `S1_llm_only` | `canonical_fact` | `'has_observed_vertical_extent'}` | {'label': 'SFC/FL170', 'type': 'flight_level_range'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL170 |
| `cand-eb310468619726f5` | `S1_llm_only` | `canonical_fact` | `'was_detected_at'}` | {'label': '14/1030Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EM DETECTED EST VA DTG: 14/1030Z |
| `cand-f2e163f78efa3fbe` | `S1_llm_only` | `canonical_fact` | `'has_source_elevation'}` | {'label': '15256 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 15256 FT AMSL |

## ATCSCC-GOLD-048 / 2026-05-17:003

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=3
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 16

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-171200 SIGNATURE: 26/05/17 00:43 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08138ecf1101f27b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 3 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION |
| `cand-1d8cd86549ae6f4f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-17T00:43:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-17120... |
| `cand-20b466decc9436fd` | `S1_llm_only` | `canonical_fact` | `'state'}` | {'label': 'closed', 'type': 'status'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. |
| `cand-217db584d98a952c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170043-171200 |
| `cand-2c79096a71c90f05` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-17120... |
| `cand-314d92c01c7d5641` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-36abb1ca8be75a12` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-3764a46d20692fd9` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-3f7bf62e61052804` | `S1_llm_only` | `canonical_fact` | `'instruction'}` | {'label': 'normal ATCSCC phone lines', 'type': 'contact method'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-50eaa031cd2ea326` | `S1_llm_only` | `canonical_fact` | `'time interval'}` | {'label': '170043-171200', 'type': 'time interval'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-6e1f1ffd0d3e29f2` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 3 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-17120... |
| `cand-6f22109771e33824` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170043-171200 |
| `cand-ab7a06497b76b3d1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-17T00:43:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 00:43 |
| `cand-d3630610b6ee889d` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-17120... |
| `cand-d3ab2bd1dd1c96d7` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 3 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION |
| `cand-ff46fc1ce4f832c7` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-17120... |

## ATCSCC-GOLD-049 / 2026-05-19:013

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=13
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
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
| `cand-02f1d920ea9e662d` | `S1_llm_only` | `canonical_fact` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '19/1800Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/1800Z NO VA EXP |
| `cand-059b1a847219f77d` | `S1_llm_only` | `canonical_fact` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '20/0000Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/0000Z NO VA EXP |
| `cand-108d2f7f17640892` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 13 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-16093312a035c2f5` | `S1_llm_only` | `canonical_fact` | `'not_identifiable_from_satellite_data'}` | {'class': 'Observation result', 'name': 'VA NOT IDENTIFIABLE FM STLT DATA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: VA NOT IDENTIFIABLE FM STLT DATA |
| `cand-16c8dc0874495318` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-20df0c4770a4dc72` | `S1_llm_only` | `canonical_fact` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '19/1200Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/1200Z NO VA EXP |
| `cand-3873befd0a489fab` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-53f8cfb949650db6` | `S1_llm_only` | `canonical_fact` | `'located_in_area'}` | {'class': 'Geographic Area', 'name': 'MEXICO'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: MEXICO |
| `cand-62183d6e0fb0bcd4` | `S1_llm_only` | `canonical_fact` | `'identifies_volcano'}` | {'class': 'Volcano', 'name': 'POPOCATEPETL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-6ce23877abf8d8f2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T06:06:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 06:09 |
| `cand-77471b3a8ee27dde` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T06:09:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 06:09 |
| `cand-89f6a94bb620ddcf` | `S1_llm_only` | `canonical_fact` | `'reports_steam_gas_only_currently'}` | {'class': 'Emission type', 'name': 'STEAM/GAS EMS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WEBCAM SHOWS ONLY STEAM/GAS EMS CURRENTLY. |
| `cand-9d389c713999340b` | `S1_llm_only` | `canonical_fact` | `'reported_source_elevation'}` | {'class': 'Elevation', 'name': '17693 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 17693 FT AMSL |
| `cand-a28f8fe057d6dea8` | `S1_llm_only` | `canonical_fact` | `'warns_new_ash_emission_possible_any_time'}` | {'class': 'Probability statement', 'name': 'NEW VA EMS LIKELY AT ANY TIME'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW VA EMS LIKELY AT ANY TIME. |
| `cand-a328b5c1d0380afb` | `S1_llm_only` | `canonical_fact` | `'ended_at_observation_time'}` | {'class': 'Observation Time', 'name': '19/0551Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS ENDED OBS VA DTG: 19/0551Z |
| `cand-bc821fe6580fee6e` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 13 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-c6c154046040b81a` | `S1_llm_only` | `canonical_fact` | `'indicates_not_detected_on_satellite_products'}` | {'class': 'Observation summary', 'name': 'VA NOT DETECTED ON VARIOUS STLT PRODUCTS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: VA NOT DETECTED ON VARIOUS STLT PRODUCTS. |
| `cand-d28a03dd5916288d` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-db13defb0c82d7f1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-f84d3921e54211fe` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |

## ATCSCC-GOLD-050 / 2026-05-19:043

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=43
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 191422 WSI DDS:191425 VA ADVISORY DTG: 20260519/1422Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/582 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: FRQT VA EMS OBS VA DTG: 19/1350Z OBS VA CLD: SFC/FL150 N1429 W09052 - N1427 W09053 - N1415 W09158 - N1429 W09209 - N1429 W09052 MOV SW 15KT FCST VA CLD +6HR: 19/2000Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1402 W09156 - N1416 W09208 - N1429 W09053 FCST VA CLD +12HR: 20/0200Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1404 W09158 - N1420 W09208 - N1429 W09053 FCST VA CLD +18HR: 20/0800Z SF...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04299106baecec89` | `S1_llm_only` | `canonical_fact` | `has_volcano_identifier` | 342090 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 |
| `cand-1748354d26606758` | `S1_llm_only` | `canonical_fact` | `estimated_extent_from_summit` | approx 70 NM WSW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXTG APPRX 70 NM WSW FM SUMMIT |
| `cand-1e59bba76c557898` | `S1_llm_only` | `canonical_fact` | `has_advisory_number` | 2026/582 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/582 |
| `cand-22ec16a2658812cb` | `S1_llm_only` | `canonical_fact` | `expected_shift_by_time_horizon` | shift SW by T+18 HRS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WSW MVMT EXP TO SHIFT SW BY T+18 HRS |
| `cand-26505a51e8da3bc4` | `S1_llm_only` | `canonical_fact` | `has_source_elevation` | 12346 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-303a63bb0d096eb8` | `S1_llm_only` | `canonical_fact` | `eruption_activity_description` | FRQT VA EMS OBS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: FRQT VA EMS OBS |
| `cand-319ef57f78332c7e` | `S1_llm_only` | `canonical_fact` | `has_advisory_date_time` | 20260519/1422Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260519/1422Z |
| `cand-4dedb5c38e250e6e` | `S1_llm_only` | `canonical_fact` | `observed_in` | WEBCAM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBSD IN WEBCAM |
| `cand-4eaa09c8586fc0ae` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-5c4e9ac75fba9220` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 43 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/582 |
| `cand-6aad154464b98b10` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T14:25:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:25 |
| `cand-8320c7006342b665` | `S1_llm_only` | `canonical_fact` | `observed_in` | STLT IMG | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBSD IN WEBCAM AND STLT IMG |
| `cand-8384b05341be71e2` | `S1_llm_only` | `canonical_fact` | `based_on` | WEBCAM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-87bb111e97f8498d` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 43 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-89bd307ae9d1d5ee` | `S1_llm_only` | `canonical_fact` | `observation_time` | 19/1350Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 19/1350Z |
| `cand-92184801dc9ef3ac` | `S1_llm_only` | `canonical_fact` | `has_advisory_title` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-935e2f841e7d5561` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T14:22:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 14:25 |
| `cand-93db1e68bfca7bac` | `S1_llm_only` | `canonical_fact` | `based_on` | NWP MDLS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-9e7b93f320438d90` | `S1_llm_only` | `canonical_fact` | `based_on` | STLT OBS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-afaf801c0d8dc4eb` | `S1_llm_only` | `canonical_fact` | `observed_movement_direction` | SW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 15KT |
| `cand-b07a0149bc89bc49` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-b09e7ac4ca29c533` | `S1_llm_only` | `canonical_fact` | `observed_flight_level_range` | SFC/FL150 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 |
| `cand-b1f60397af7edbf3` | `S1_llm_only` | `canonical_fact` | `observed_movement_speed` | 15KT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 15KT |
| `cand-cf92eb9bbb161e1a` | `S1_llm_only` | `canonical_fact` | `is_reported_by` | WASHINGTON VAAC | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: WASHINGTON |
| `cand-db6c88d073002906` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-de7615779fe65b41` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-e4f2d514353b927d` | `S1_llm_only` | `canonical_fact` | `is_located_in_area` | GUATEMALA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: GUATEMALA |
| `cand-eb82000d3b8597b5` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-fa1b8ebb4188190d` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 43 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
