# NASA ATMONTO Gold Review batch_01

- Samples: `ATCSCC-GOLD-001` to `ATCSCC-GOLD-010`
- Records: 10
- Candidate clusters: 318

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-001 / 2026-05-19:032

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=32
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 35

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. EFFECTIVE TIME: 191322-191630 SIGNATURE: 26/05/19 13:22 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03980efdeb6e9215` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-092d47690b54cb8b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THAT | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-0956f4acebbd46c2` | `S1_llm_only` | `canonical_fact` | `has advisory title` | DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-0c293b3a62114ee0` | `S1_llm_only` | `canonical_fact` | `replaces advisory` | 027 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY REPLACES ADVZY 027 |
| `cand-26248cca7b96a8f7` | `S1_llm_only` | `canonical_fact` | `encouraged action` | file alternate routes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. |
| `cand-2a5e39256de37832` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-2eb7db50e5f7e305` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ARE | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-3470caf9720e03ce` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T13:22:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-3e78fc365dd21aee` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-3e8ed1851904958f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T16:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191322-191630 |
| `cand-48ee85e1e5be8dd1` | `S1_llm_only` | `canonical_fact` | `cause stated in advisory` | severe turbulence | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-5452139e1194c658` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADVZY | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-580069f2df1cb6f9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:AR8 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-5f88b556258bb0b4` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 32 | `{"repaired_accepted": 1}` | `{}` | ZNY REPLACES ADVZY 027 |
| `cand-61c8e7ec09b3ca1e` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-64f6e977c8b8b2b8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T13:22:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191322-191630 |
| `cand-665a5be97a6969ae` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 32 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-6db320888d86cf81` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:L454 | `{"hybrid_backbone_accepted": 2, "repaired_accepted": 2}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-7ca7a8175b5dcbba` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-7e9c1410238dbb41` | `S1_llm_only` | `canonical_fact` | `effective time` | 191322-191630 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191322-191630 |
| `cand-858a5b29bd3619df` | `S1_llm_only` | `canonical_fact` | `advises route closure` | L452 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-86ca9275f3059e2f` | `S1_llm_only` | `canonical_fact` | `advises route closure` | L454 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-8bca18b88e693850` | `S1_llm_only` | `canonical_fact` | `advises route closure` | AR8 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-8d1b462e960d741a` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-8dfa6e571ced77bf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T13:22:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 13:22 |
| `cand-8f22a524e366583a` | `S1_llm_only` | `canonical_fact` | `reports event time window` | 19/1200 - 19/1600 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/1200 - 19/1600 |
| `cand-9f7c702c3489fb66` | `S1_llm_only` | `canonical_fact` | `names constrained facility` | ZNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-a30425c30c41b509` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | severe turbulence | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-a3f41e32e500c1e4` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-c03e0e96bf714bf5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADDS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-c1de08278625081b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:L452 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-d5044991bcb5608b` | `S1_llm_only` | `canonical_fact` | `adds route` | L454 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDS L454 |
| `cand-dd73696174e72a7b` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE... | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TU... |
| `cand-ec3d65f234308d7e` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 32 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-f581456c98fbad41` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |

## ATCSCC-GOLD-002 / 2026-05-15:063

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=63
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 15/1918 - 16/0000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 151918-160030 SIGNATURE: 26/05/15 19:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03d2b704d6be0b1c` | `S1_llm_only` | `canonical_fact` | `can_expect` | airborne holding into San Diego Airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT |
| `cand-161d19bb2457224a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-2a48e7bbcc59050a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:18:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-2cd6d1eb74d6c128` | `S1_llm_only` | `canonical_fact` | `are_due_to` | compacted demand | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-31061102a9a4c8ce` | `S1_llm_only` | `canonical_fact` | `can_expect` | arrival delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT |
| `cand-33d28dbc7c892558` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T00:00:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-3672d79202199bb9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-15T19:18:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 19:18 |
| `cand-480627a568804dc1` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-4b0313b23f63448b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-62104fae3fc48981` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-765670f6e4fa2213` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T00:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-81dac5edcd117771` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 63 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-872a90f29c295367` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:18:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-875ea39dcff9a520` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-8b24911961d6ec51` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-15T19:18:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 19:18 |
| `cand-91e158e08a15dbda` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:18:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-b3ef4114981bc2fd` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | San Diego Airport | `{"repaired_accepted": 1}` | `{}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-b45d13444bd57cc8` | `S1_llm_only` | `canonical_fact` | `have_maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-b4f391faf4ce0c38` | `S1_llm_only` | `canonical_fact` | `announces` | SAN airport arrival delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-cbe6cb9e8f529674` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SAN | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-d99125d7e166cbff` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | volume | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-dcfd8a9f849d6e78` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | SAN Airport | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-e2a1b014664055e9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DIEGO | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-e33d82cdf5f8ea54` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-e517d0ce120e6c3e` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 63 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-e5a671e3e01f06a8` | `S1_llm_only` | `canonical_fact` | `has_time_span` | 15/1918 - 16/0000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 15/1918 - 16/0000 |
| `cand-ec55bc9996a5e532` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | Users can expect arrival delays / airborne holding into San Diego Airport of up to 30 minutes due to compacted demand. Updates will follow if necessary. | `{"repaired_accepted": 1}` | `{}` | MESSAGE: EVENT TIME: 15/1918 - 16/0000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-f179f8ec46ba0510` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T00:30:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-f44ec5879948c238` | `S1_llm_only` | `canonical_fact` | `will_follow_if_necessary` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |

## ATCSCC-GOLD-003 / 2026-05-18:069

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=69
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 18/1545 - 18/2000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 181545-182030 SIGNATURE: 26/05/18 15:45 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-120cdf0b1c721a94` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-1c20a51d704da888` | `S1_llm_only` | `canonical_fact` | `'can_expect_arrival_delays_or_airborne_holding'}` | {'type': 'delay_duration', 'value': 'up to 30 minutes'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-1e26b75fad279cbf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-2a7d43ffe301b8fc` | `S1_llm_only` | `canonical_fact` | `'caused_by'}` | {'type': 'demand_condition', 'value': 'compacted demand'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-38785d11ab0ada24` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T15:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181545-182030 |
| `cand-4760f2ad6956d861` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T20:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181545-182030 |
| `cand-4ed4d7dac9c4fde3` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | volume | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. |
| `cand-57de26e503671d37` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-618359e579b914f6` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 69 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. |
| `cand-70163bcbdf393132` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-7716781deb55b778` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-7a26d7e447f9e5fb` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | LAS Vegas Airport | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. |
| `cand-7c2f15b6de0c86cf` | `S1_llm_only` | `canonical_fact` | `'runs_to'}` | {'type': 'timestamp', 'value': '18/2000'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1545 - 18/2000 |
| `cand-7ec71a9c623357bd` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:VEGAS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-8c05d0dab8abcd27` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | compacted demand demand_condition | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | DUE TO COMPACTED DEMAND |
| `cand-8fa6b710bd1d5da8` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 69 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-94d9fa191e3139b0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:VEGAS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-95d49a54ce077cd4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T15:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 15:45 |
| `cand-9c2113d012bc7d9d` | `S1_llm_only` | `canonical_fact` | `'runs_from'}` | {'type': 'timestamp', 'value': '18/1545'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1545 - 18/2000 |
| `cand-aa1999464457c499` | `S1_llm_only` | `canonical_fact` | `'announces_airport_arrival_delays'}` | {'type': 'airport', 'value': 'Las Vegas Airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-ae202e6c578cf9f7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-bcda714224529b46` | `S1_llm_only` | `canonical_fact` | `'promises_follow_up_updates_if_necessary'}` | {'type': 'update_notice', 'value': 'updates'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-c9b58e4bd35b66f9` | `S1_llm_only` | `canonical_fact` | `'ends_at'}` | {'type': 'timestamp', 'value': '182030'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181545-182030 |
| `cand-fcf62c6b906576d7` | `S1_llm_only` | `canonical_fact` | `'starts_at'}` | {'type': 'timestamp', 'value': '181545'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181545-182030 |

## ATCSCC-GOLD-004 / 2026-05-14:059

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=59
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 36

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ EFFECTIVE TIME: 141554-150100 SIGNATURE: 26/05/14 15:54 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05dd9896c47dbe78` | `S1_llm_only` | `canonical_fact` | `include_airports` | CDW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-081409a19a4378e1` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LDJ | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-0bbd1b59e59fe3b9` | `S1_llm_only` | `canonical_fact` | `include_airports` | TEB | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-1410476fe2bcda19` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T01:00:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWA... |
| `cand-1e4fba32b4173686` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:AND | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-38e5510e0e91a92a` | `S1_llm_only` | `canonical_fact` | `identifies_event_time_window` | 14/1700 - 15/0100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/1700 - 15/0100 |
| `cand-470cc2f9b16bac62` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | LOW | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWA... |
| `cand-4f39e89cea945d3e` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:TEB | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-57a317dce08fb9ee` | `S1_llm_only` | `canonical_fact` | `are_due_to` | compacted demand | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-57c974c97ed81aad` | `S1_llm_only` | `canonical_fact` | `include_airports` | LDJ | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-57fedf1035dd8294` | `S1_llm_only` | `canonical_fact` | `names_constrained_facility_area` | ZNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-5f0a41c1b63f8abb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-14T15:54:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 15:54 |
| `cand-6203c4af64f5d13a` | `S1_llm_only` | `canonical_fact` | `promises_updates` | will follow if necessary | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-630c6bc8d4872b95` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 59 | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-632776e237be985f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:54:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-663abc1431a9004e` | `S1_llm_only` | `canonical_fact` | `states_event_title` | EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-688b63b83e7e709a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-6e3fae232428f706` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T15:54:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWA... |
| `cand-6f0b917db886a229` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDW | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-74943c40174a0219` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T15:54:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141554-150100 |
| `cand-7ef12c8f255a55d3` | `S1_llm_only` | `canonical_fact` | `can_expect_arrival_delays_and_airborne_holding_into` | Newark and Newark satellite airports | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS |
| `cand-862daff7ccf60ce2` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-8cd2f614737f070c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T01:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141554-150100 |
| `cand-991ef3be833b58fb` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FO... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-993bcc8939caff82` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FO... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWA... |
| `cand-9a29660c620c0051` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-9b2c16c450ce3e2a` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 59 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWA... |
| `cand-a7429d149fe9768e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-b2e6dbd780a6b160` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T01:00:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-da48274e4242a4bf` | `S1_llm_only` | `canonical_fact` | `have_reported_maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OF UP TO 30 MINUTES |
| `cand-dad475c94e2a63a1` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 59 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-de4e272d7f9695e7` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T17:00:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWA... |
| `cand-ea9f08b0c6952725` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MMU | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-ed0214bafea35c13` | `S1_llm_only` | `canonical_fact` | `include_airports` | MMU | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-ed4ae12b703cde6e` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {"@type": "nas:Airport", "evidence_text": "EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS"} | `{"repaired_accepted": 1}` | `{}` | EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-eeaf7c3ed2af20f8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |

## ATCSCC-GOLD-005 / 2026-05-19:059

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=59
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI MESSAGE: EVENT TIME: 19/1645 - 20/0200 CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 191638-200230 SIGNATURE: 26/05/19 16:38 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0517cad842649dbd` | `S1_llm_only` | `canonical_fact` | `'identifies constrained facilities'}` | {'label': 'ZHU'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-111a6499cbba4202` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | IAH | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-15984c6fdfc39bac` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |
| `cand-1e88b97468decda4` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-2362f4bf93684b17` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T16:38:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 16:38 |
| `cand-277fc4749cecc5eb` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-289969c1f4645e7e` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-19T16:38:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 16:38 |
| `cand-2e547f4468922131` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-480afcfebd3554b8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |
| `cand-5186fbd53e9413e4` | `S1_llm_only` | `canonical_fact` | `'states event time'}` | {'label': '19/1645 - 20/0200'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/1645 - 20/0200 |
| `cand-5caff5616d01f5c7` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-66f3229b06234ca5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191638-200230 |
| `cand-671bc36b93bd6cd2` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `type` | atm:ReRouteTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-6990fc891f53af26` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-70b4871b899569dc` | `S1_llm_only` | `canonical_fact` | `'reason stated as'}` | {'label': 'weather'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-71dfdccd99e7fea5` | `S1_llm_only` | `canonical_fact` | `'mentions locations'}` | {'label': 'IAH HOU'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-772e6ac83353df92` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | HOU | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-82698dbeb4a7898a` | `S1_llm_only` | `canonical_fact` | `'states effective time'}` | {'label': '191638-200230'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191638-200230 |
| `cand-930af7acc8fde85c` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | FYI | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-9658a4068d877207` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-a053fc88bf21f0a2` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T16:38:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-a3505e8fbde44beb` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 59 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-a763979cb20caafd` | `S1_llm_only` | `canonical_fact` | `'gives operational instruction'}` | {'label': 'users should fuel accordingly'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-ac95c2adb307c435` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 59 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-b0b0983cc362175b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T16:38:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191638-200230 |
| `cand-c7e1fe829757e7ed` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteType` | CDR | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-cf01fa3c2f697eb2` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteReason` | WEATHER | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-f26e6771005f30d4` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T16:38:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-f9349a7d3276cb43` | `S1_llm_only` | `canonical_fact` | `'is implementing'}` | {'label': 'CDRS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |

## ATCSCC-GOLD-006 / 2026-05-19:144

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=144
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED MESSAGE: EVENT TIME: 19/2230 - 20/0300 CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. EFFECTIVE TIME: 192220-200330 SIGNATURE: 26/05/19 22:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04805052cd09aac5` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 144 | `{"repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-07fcb2a51ff11716` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T03:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-0e6136a9ee951b64` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T22:20:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 22:20 |
| `cand-20aaa73732c84b2f` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T03:30:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-23192b28e9c65220` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DROP | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-2cd2d23d5bc07f99` | `S1_llm_only` | `canonical_fact` | `'causes flight plan drop times to be generated from'}` | {'class': 'traffic_management_time', 'label': 'EDCT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-43633790f4569b9a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:HAS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-510ff876261f5354` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 144 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-5187786950bf28bb` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP... | `{"repaired_accepted": 1}` | `{}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-532c30b99c554ecc` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T22:20:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-6ed0a8b756a2cd15` | `S1_llm_only` | `canonical_fact` | `'has implemented'}` | {'class': 'operational_procedure', 'label': 'extended flight plan drop times'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-71e5beec96521a52` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | edct | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-72a5ec1771afe01a` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | ZBW | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW |
| `cand-7f528fc47a311528` | `S1_llm_only` | `canonical_fact` | `'triggered by condition'}` | {'class': 'unspecified_cause', 'label': 'XXX'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. |
| `cand-878c9beec21df694` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PLAN | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-889de63fe5b6bfea` | `S1_llm_only` | `canonical_fact` | `'set to duration'}` | {'class': 'time_duration', 'label': '180 minutes'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-8941d7b4003417d3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:TIMES | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-a54d42868f9a3c8b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-a5f63fb15fa09b2c` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP... | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-a7c0f23db3ee4f27` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T22:20:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-b3fbdcb7ad0f28bc` | `S1_llm_only` | `canonical_fact` | `'are generated from'}` | {'class': 'traffic_management_time', 'label': 'EDCT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-b846a5b4b5b8a624` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-19T22:20:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-e9e3b11500230eb2` | `S1_llm_only` | `canonical_fact` | `'announces'}` | {'class': 'operational_action', 'label': 'extended flight plan drop times implemented'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-fe10f1cc9f81bc7b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T22:20:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 22:20 |

## ATCSCC-GOLD-007 / 2026-05-16:051

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=51
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI MESSAGE: EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 161818-162330 SIGNATURE: 26/05/16 18:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0c088a95e7679b2c` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-110225132c4a0b95` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T18:18:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-15ebd3b576826e70` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:ARTCC/DCC | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-219764c5542242ba` | `S1_llm_only` | `canonical_fact` | `instruction` | fuel accordingly | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-332f96f27ff8beef` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-16T18:18:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 18:18 |
| `cand-40dffe40a1f1dab8` | `S1_llm_only` | `canonical_fact` | `identifies_constrained_facility` | ZDV | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-4e533db99ede08c6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |
| `cand-4fb8b477200680d2` | `S1_llm_only` | `canonical_fact` | `is_implementing` | CDRS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-4ff32413bc899986` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteReason` | WEATHER | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-5ea2f433986c589d` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |
| `cand-8420637a7cd9ed9e` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 51 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-88dcd1805977bd29` | `S1_llm_only` | `canonical_fact` | `states_effective_time_window` | 161818-162330 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161818-162330 |
| `cand-8d39633573e323b4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T23:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-968cbd944ded5179` | `S1_llm_only` | `canonical_fact` | `has_reason` | weather | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-9d8a1af80687c131` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteType` | CDR | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-a7ef25f094c64770` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:ARTCC/ZDV | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-ad7c43de63c7f183` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-adb4df67cbb52ff9` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T23:30:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-be0993666da8b7e4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 51 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-c7a09d343923fb39` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | FYI | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-c96f1aa8e96010a0` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T18:18:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 18:18 |
| `cand-d0acc6f7a4bc1f7e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T18:18:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-e1c52dcc55e64299` | `S1_llm_only` | `canonical_fact` | `states_event_time_window` | 16/1818 - 16/2300 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1818 - 16/2300 |
| `cand-e4ee9f8f5182942e` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZDV |

## ATCSCC-GOLD-008 / 2026-05-17:019

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=19
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES EFFECTIVE TIME: 171218-171645 SIGNATURE: 26/05/17 12:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-032f90fe7dacf76e` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T12:18:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-04b4c63ca25d34cb` | `S1_llm_only` | `canonical_fact` | `'arrival delays / airborne holding'}` | {'label': 'arrival delays and airborne holding', 'value': 'ARRIVAL DELAYS / AIRBORNE HOLDING'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-0cd464692e410cf2` | `S1_llm_only` | `canonical_fact` | `'if necessary'}` | {'label': 'future updates', 'value': 'UPDATES'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-18cfe2c69d11db5b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SOUTH | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-1c54f73133d57355` | `S1_llm_only` | `canonical_fact` | `'arrival delays / airborne holding'}` | {'label': 'arrival delays and airborne holding', 'value': 'ARRIVAL DELAYS / AIRBORNE HOLDING'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UP TO 30 MINUTES DUE TO THUNDERSTORMS |
| `cand-1e1eaff26ce4b9c9` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SOUTH | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-27b791583ea5915d` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-17T12:18:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-3720bc93f718ea2e` | `S1_llm_only` | `canonical_fact` | `'up to 30 minutes'}` | {'label': 'delay duration', 'value': 'UP TO 30 MINUTES'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-3edf3c9c07ff5814` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:FLL | `{"repaired_accepted": 1}` | `{}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-44cee5f9e12996db` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THE | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-4bf34f910edf3e9a` | `S1_llm_only` | `canonical_fact` | `'arrival delays'}` | {'label': 'South Florida airports', 'value': 'SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| `cand-4d0bcf4fa8e23773` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-5e2094d4220b3723` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T16:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171218-171645 |
| `cand-77e5b25b4e2f8b15` | `S1_llm_only` | `canonical_fact` | `'South Florida airports'}` | {'label': 'South Florida airports', 'value': 'THE SOUTH FLORIDA AIRPORTS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-7c5f79007b5d369e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-801500c7f58618af` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PBI | `{"repaired_accepted": 1}` | `{}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-864aab1f1a580945` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THEIR | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-8bb374499214d1c0` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-9c542e3fba3413bb` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | FLL | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-aa85f35c5c6147b2` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-b80eea9e547c8542` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-bf2b44e46daa419c` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 19 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-c0cd6e01b50c5edf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T12:18:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171218-171645 |
| `cand-c3dffb3f22541108` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T16:45:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-cd716badd6aeb1e3` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 19 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| `cand-d1c94018f9f4739c` | `S1_llm_only` | `canonical_fact` | `'MIA, PBI, FLL and their satellites'}` | {'label': 'example airports and satellites', 'value': 'MIA, PBI, FLL AND THEIR SATELLITES'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-d3e8bb99475ab904` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MIA | `{"repaired_accepted": 1}` | `{}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-ec4eda07e331fc6d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-17T12:18:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 12:18 |
| `cand-ec7cb3d0943cc049` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | PBI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-f3caf03d39285ad3` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | MIA | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AI... |
| `cand-fbbabde071eaf701` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY... | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NE... |
| `cand-fcac0a97251ab71b` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | arrival delays and airborne holding arrival delays / airborne holding | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | UP TO 30 MINUTES DUE TO THUNDERSTORMS |
| `cand-fd0683497e7e907a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |

## ATCSCC-GOLD-009 / 2026-05-20:040

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=40
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 38

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201400 PROBABILITY OF EXTENSION: MODERATE REMARKS: ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < REDDN4 KMCO KORL KSFB ZMA KDFW >JAWJA MGMRY SARKK YUYUN < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA MGMRY SARKK PUDJE < REDDN4 TMI ID: RRDCC504 EFFECTIVE TIME: 201000-201400 SIGNAT...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-10a79bfcc41f76cc` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-19e5112d9c18f569` | `S1_llm_only` | `canonical_fact` | `contains_route` | {'destination': 'KDAL', 'origin': 'KMCO', 'route': '>JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS |
| `cand-1e55c9d11fad4b64` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 40 | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-1e6a57dc4419d7ea` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-1f1bfc56f641d24a` | `S1_llm_only` | `canonical_fact` | `contains_route` | {'destination': 'KDFW', 'origin': 'KMCO', 'route': '>JAWJA MGMRY SARKK YUYUN'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDFW >JAWJA MGMRY SARKK YUYUN |
| `cand-2b343e95dbbd5278` | `S1_llm_only` | `canonical_fact` | `contains_route` | {'destination': 'KDFW', 'origin': 'KMCO', 'route': '>JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS |
| `cand-2e0f46a084b773fe` | `S1_llm_only` | `canonical_fact` | `flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-4e8ef2e6e542643a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T10:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201400 |
| `cand-583fe080fae3458a` | `S0_rule_only, S1b_llm_canonicalized` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-58e1622086806d8c` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-5e15e959873d8035` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZH... | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-5f5aea3d0091bcda` | `S1_llm_only` | `canonical_fact` | `has_name` | FLORIDA_TO_TEXAS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: FLORIDA_TO_TEXAS |
| `cand-68c31f8d5b6bbd72` | `S1_llm_only` | `canonical_fact` | `probability_of_extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-714490a80e967b05` | `S1_llm_only` | `canonical_fact` | `facilities_included` | ['ZFW', 'ZHU', 'ZJX', 'ZMA', 'ZME', 'ZTL'] | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-778af5a10a3efb1f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T21:40:00 | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-7dd1801f6933f4a8` | `S1_llm_only` | `canonical_fact` | `contains_route` | {'destination': 'KDAL', 'origin': 'KMCO', 'route': '>JAWJA MGMRY SARKK PUDJE'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDAL >JAWJA MGMRY SARKK PUDJE |
| `cand-7fe14b7bcb284c7a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-20T09:42:00 | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-8961e6f5af8f998e` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-89b2e71645d03738` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-8f0352d8836ca88f` | `S1_llm_only` | `canonical_fact` | `has_constrained_area` | ZHU | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZHU |
| `cand-9372ccfe8e0cf13f` | `S1_llm_only` | `canonical_fact` | `has_tmi_id` | RRDCC504 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC504 |
| `cand-9b741ec78d3ba0a5` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:KDAL | `{"repaired_accepted": 1}` | `{}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-9f28201aa744eb56` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-a3ab399d14ba65b6` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-b27d538207b95c0c` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-c26ad4906394c509` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:KDFW | `{"repaired_accepted": 1}` | `{}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-c6dbeee9c81e7dd6` | `S1_llm_only` | `canonical_fact` | `traffic_departures_to` | ['KDAL', 'KDFW'] | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-d055d0fd5785866d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T09:42:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 09:42 |
| `cand-d23f81e142e0cf1e` | `S1_llm_only` | `canonical_fact` | `valid_time_window` | ETD 201000 TO 201400 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201400 |
| `cand-d70b2b9465df72db` | `S1_llm_only` | `canonical_fact` | `includes_traffic` | ['KMCO', 'KORL', 'KSFB', 'ZMA'] | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-da648db2a59231f9` | `S1_llm_only` | `canonical_fact` | `effective_time_window` | 201000-201400 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201000-201400 |
| `cand-dae2c1f9cec589a5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T14:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201400 |
| `cand-db974e25d7f0c051` | `S1_llm_only` | `canonical_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-dec998ca4d2499fa` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 40 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-ea11f1a110777bb8` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-f47eb5038aeb111d` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-f9abdecb067cb7c3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |
| `cand-fdd4c0108d8964a9` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:10:00 | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 2010... |

## ATCSCC-GOLD-010 / 2026-05-20:053

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=53
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 46

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201700 PROBABILITY OF EXTENSION: MODERATE REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < REDDN4 TMI ID: RRDCC504 EFFECTIVE TIME: 201000-201700 SIGNATURE: 26/05/20 12:48 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| C...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0e34ab120d1c0f88` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201... |
| `cand-23c53352b6f57970` | `S0_rule_only, S1b_llm_canonicalized` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-2796068438874849` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-3147d2bc3c99fb1b` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-31d7569c24391a8f` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201... |
| `cand-32a45098e70cf94f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-38efe07fbb569e1c` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-4c63d776ff1ba302` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-4d243e73d8ee2637` | `S1_llm_only` | `canonical_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-51e16de460e365c5` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201... |
| `cand-5d968ed5fc68468f` | `S1_llm_only` | `canonical_fact` | `valid_from` | 201000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201700 |
| `cand-63a04c722f0d412e` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-672a6392c904970a` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T12:48:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-6c7e9b9bba843607` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:10:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-81cba67748da78d3` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-888fa66ea6c40581` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 53 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-937f8f3fecf9545b` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201... |
| `cand-9ed23d71fb84d59b` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T17:00:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-9f5fc1dcf334f02c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T17:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201700 |
| `cand-a6aee0d5d0d3cfde` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-a9fce8d43f2bffe3` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | REPLACES ADVZY 042, EXTENDS END TIME. | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201... |
| `cand-ae01b2d49eebda77` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-b7445d154db243e8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T10:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201700 |
| `cand-ba13444684174556` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-ba2fe74ef9dcaecc` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-bbbf26e5771f305a` | `S1_llm_only` | `canonical_fact` | `valid_to` | 201700 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201700 |
| `cand-bc7d2c9195ad7ad6` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T21:70:00Z | `{"rejected_schema": 1}` | `{"datatype_value_not_datetime": 1}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-bc89c9601d92aee8` | `S1_llm_only` | `canonical_fact` | `has_constrained_area` | ZHU | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZHU |
| `cand-bcf12693b24285f5` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-bf003dc3fe2121d9` | `S1_llm_only` | `canonical_fact` | `includes_traffic` | KMCO/KORL/KSFB/ZMA departures to KDAL/KDFW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-c987225a8def3deb` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-cb10468ef23ec5db` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T12:48:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 12:48 |
| `cand-cc1e4f5b7bed5f0f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-20T12:48:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-cc8610ff36466fb3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:10:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-cfe262958628eb81` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-d52232757d2a9709` | `S1_llm_only` | `canonical_fact` | `replaces_advisory` | ADVZY 042 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-d550f6cf56ce61f6` | `S1_llm_only` | `canonical_fact` | `has_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-da22912b0e79a270` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-e7cec40e0b2251a6` | `S1_llm_only` | `canonical_fact` | `is_named` | FLORIDA_TO_TEXAS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: FLORIDA_TO_TEXAS |
| `cand-ecbdbad34f80facf` | `S1_llm_only` | `canonical_fact` | `has_effective_time_range` | 201000-201700 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201000-201700 |
| `cand-efcb10fc1b6a4d21` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 53 | `{"repaired_accepted": 1}` | `{}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-f267f6ac5624b821` | `S1_llm_only` | `canonical_fact` | `has_facilities_included` | ZFW/ZHU/ZJX/ZMA/ZME/ZTL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-f3558c62a10d7ece` | `S1_llm_only` | `canonical_fact` | `extends_end_time` | true | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-f563ac8dc2cdde21` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | REPLACES ADVZY 042, EXTENDS END TIME. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/... |
| `cand-f747e6a3206f52b2` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-fcfa79f240a9db1a` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
