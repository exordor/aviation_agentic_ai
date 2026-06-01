# NASA ATMONTO Gold Review batch_07

- Samples: `ATCSCC-GOLD-061` to `ATCSCC-GOLD-070`
- Records: 10
- Candidate clusters: 263

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-061 / 2026-05-15:017

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=17
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA MESSAGE: FVXX22 KNES 150845 WSI DDS:150847 VA ADVISORY DTG: 20260515/0845Z VAAC: WASHINGTON VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS SOURCE ELEV: 4009 FT AMSL ADVISORY NR: 2026/025 INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. NWP MODELS. ERUPTION DETAILS: ERUPTION CONTINUES OBS VA DTG: 15/0826Z OBS VA CLD: SFC/FL100 N1931 W15526 - N1926 W15517 - N1924 W15516 - N1921 W15532 - N1931 W15526 MOV W 10KT SFC/FL200 N2013 W15354 - N2002 W15347 - N1940 W15435 - N1946 W15444 - N2013 W15354 MOV NE 20KT FCST VA CLD +6HR: 15/1430Z SFC/FL100 N1943 W15534 - N1926 W15516 - N1924 W15516 - N1907 W15543 - N1943 W15534 SFC/FL200 NO VA...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0d1f43c517bbdeb8` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | Kilauea | `{"repaired_accepted": 1}` | `{}` | VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS |
| `cand-108494ba1264d2ba` | `S1_llm_only` | `canonical_fact` | `expected ash presence` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/2030Z NO VA EXP |
| `cand-1b660b1cb4b21cc6` | `S1_llm_only` | `canonical_fact` | `were dispersing` | toward the southwest farther from summit | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISPERSING TWD THE SW FURTHER FM SUMMIT |
| `cand-28d93016bdc95012` | `S1_llm_only` | `canonical_fact` | `is in area` | Hawaiian Islands | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: HAWAIIAN.IS |
| `cand-45e6319715ece211` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-15T08:47:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 08:47 |
| `cand-5cd72854c0adaad1` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 17 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-5f3f7dbc94ed165a` | `S1_llm_only` | `canonical_fact` | `observed vertical extent` | surface to FL200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SFC/FL200 |
| `cand-606de756ffa7549f` | `S1_llm_only` | `canonical_fact` | `was moving` | northeast at 20 kt | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 20KT |
| `cand-63cf3d9fa3945c31` | `S1_llm_only` | `canonical_fact` | `is continuing` | continuing | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ERUPTION CONTINUES |
| `cand-63f3b5972ae4c7fe` | `S1_llm_only` | `canonical_fact` | `expected no ash above` | FL200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SFC/FL200 NO VA EXP |
| `cand-76c1077634ae0345` | `S1_llm_only` | `canonical_fact` | `is expected to dissipate by` | T+6 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXP TO DISSIPATE BY T+6 |
| `cand-7d60da4312e3a53f` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T15:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a08c815e7597543f` | `S1_llm_only` | `canonical_fact` | `may be obscured by` | weather clouds | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FURTHER EMS MAY BE OBSC BY WX CLDS |
| `cand-a2c7d5537a96572a` | `S1_llm_only` | `canonical_fact` | `were observed on satellite` | observed on satellite | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBS ON STLT |
| `cand-a30c76196fcd7425` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-15T08:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 08:47 |
| `cand-aa3fbacf0ce685b1` | `S1_llm_only` | `canonical_fact` | `has elevation` | 4009 ft AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 4009 FT AMSL |
| `cand-b9a2bea3c521b20f` | `S1_llm_only` | `canonical_fact` | `expected vertical extent` | surface to FL100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/1430Z SFC/FL100 |
| `cand-bb259b85a74406bf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-bc3693a3ee90a31d` | `S1_llm_only` | `canonical_fact` | `is expected` | northwest movement | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NW MVMT EXP AT FL100 BY T+6 |
| `cand-c99910367d0661bc` | `S1_llm_only` | `canonical_fact` | `was observed` | off coast northeast from summit | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMNANT LGT VA CLD AT FL200 OBS OFF COAST NE FM SUMMIT |
| `cand-d28be65783d51422` | `S1_llm_only` | `canonical_fact` | `were moving` | west-northwest from summit | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVG WNW FM SUMMIT |
| `cand-e30fd2136754974a` | `S1_llm_only` | `canonical_fact` | `expected ash presence` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/0230Z NO VA EXP |
| `cand-e44b1b51712a5062` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-e4f38bb6ac9016b3` | `S1_llm_only` | `canonical_fact` | `was moving` | west at 10 kt | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV W 10KT |
| `cand-e7471e3782495cb0` | `S1_llm_only` | `canonical_fact` | `observed vertical extent` | surface to FL100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL100 |
| `cand-e8a26a4e4b2ca787` | `S1_llm_only` | `canonical_fact` | `is possible` | southwest dispersion | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WITH DISPERSION SW PSBL |
| `cand-e8e6c4f1bb3be722` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - KILAUEA | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-fdd8f03df3fd3f0b` | `S1_llm_only` | `canonical_fact` | `is the volcano named in the advisory` | Kilauea | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: KILAUEA |

## ATCSCC-GOLD-062 / 2026-05-20:029

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=29
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 200210 CCA WSI DDS:200212 VA ADVISORY -CORRECTION DTG: 20260520/0210Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/585 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 20/0140Z EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 MOV SW 10KT FCST VA CLD +6HR: 20/0730Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 FCST VA CLD +18HR:...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03539ede3acddc42` | `S1_llm_only` | `canonical_fact` | `'announces bulletin about'}` | {'label': 'volcanic activity bulletin for Fuego', 'text': 'VOLCANIC ACTIVITY BULLETIN - FUEGO'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-0b47b4c3f64a5cff` | `S1_llm_only` | `canonical_fact` | `'is located in'}` | {'label': 'Guatemala', 'text': 'AREA: GUATEMALA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-0e9c625753fcbe4c` | `S1_llm_only` | `canonical_fact` | `'forecast valid at'}` | {'label': '2026-05-20 19:30Z', 'text': '20/1930Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/1930Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09052 |
| `cand-11ee12904048f60f` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 29 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-187bdb13b579f4bd` | `S1_llm_only` | `canonical_fact` | `'gives reason'}` | {'label': 'weather clouds in summit area', 'text': 'WX CLDS IN SUMMIT AREA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-34363e02975eddb6` | `S1_llm_only` | `canonical_fact` | `'has source elevation'}` | {'label': '12346 ft amsl', 'text': 'SOURCE ELEV: 12346 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-49dbf4cffb0a7bb5` | `S1_llm_only` | `canonical_fact` | `'has correction timestamp'}` | {'label': '2026-05-20 02:10Z', 'text': 'DTG: 20260520/0210Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY -CORRECTION DTG: 20260520/0210Z |
| `cand-4bde08d0c6209e5a` | `S1_llm_only` | `canonical_fact` | `'predicts continued emissions'}` | {'label': 'likely continue', 'text': 'LIKELY CONTINUE'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-5005068bf2259314` | `S1_llm_only` | `canonical_fact` | `'has speed'}` | {'label': '10 knots', 'text': 'MOV SW 10KT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-6fc2b57d4d8e27a4` | `S1_llm_only` | `canonical_fact` | `'forecasts no change in model winds'}` | {'label': 'next 18 hours', 'text': 'NXT 18 HR'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-78637095de6c89cd` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-79d10aefbd3fde91` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-8e12432071543bd1` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-91e77062fc6ee085` | `S1_llm_only` | `canonical_fact` | `'has vertical extent'}` | {'label': 'surface to flight level 140', 'text': 'SFC/FL140'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 |
| `cand-a951d3b444750dc2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T02:10:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 02:12 |
| `cand-aedf2766318f8126` | `S1_llm_only` | `canonical_fact` | `'forecast valid at'}` | {'label': '2026-05-20 07:30Z', 'text': '20/0730Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/0730Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 |
| `cand-af732b6f50f875e3` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather clouds in summit area wx clds in summit area | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-b0221292e3ffd50f` | `S1_llm_only` | `canonical_fact` | `'estimated start time'}` | {'label': '2026-05-20 01:40Z', 'text': '20/0140Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS EST VA DTG: 20/0140Z |
| `cand-d92fa552f8a73a89` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 29 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-db9b70461b294595` | `S1_llm_only` | `canonical_fact` | `'states eruption status'}` | {'label': 'ongoing', 'text': 'ONGOING'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING |
| `cand-e8e62d03c93c4142` | `S1_llm_only` | `canonical_fact` | `'reports detection status'}` | {'label': 'not detected on satellite', 'text': 'VA NOT DETECTED ON STLT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-ee234e5421e6ffdd` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T20:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-fae275b5c2185e15` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T02:12:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 02:12 |
| `cand-fc81de610a47f111` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-fe08dda77b540b98` | `S1_llm_only` | `canonical_fact` | `'forecast valid at'}` | {'label': '2026-05-20 13:30Z', 'text': '20/1330Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 |
| `cand-fe4f6b0e2ccdec45` | `S1_llm_only` | `canonical_fact` | `'moves toward'}` | {'label': 'southwest', 'text': 'MOV SW 10KT'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |

## ATCSCC-GOLD-063 / 2026-05-16:035

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=35
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 161303-161830 SIGNATURE: 26/05/16 13:03 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0f62396c2e18bf29` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T13:03:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-1a7821ead6140d58` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | NONE | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ORD AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-1f5dde71e1dd73c5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-16T13:03:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 13:03 |
| `cand-207f4906ada6986f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-16T13:03:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 13:03 |
| `cand-3c0f298ccfc82525` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ORD AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-58cfc2ea860fe39a` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 35 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO... |
| `cand-5ed02143c4e4f8cc` | `S1_llm_only` | `canonical_fact` | `can_expect` | arrival delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-6038489c7d015554` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T13:03:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-64746e84c5d68c89` | `S1_llm_only` | `canonical_fact` | `event_time_window` | 16/1300 - 16/1800 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1300 - 16/1800 |
| `cand-6c4f9910924f2a05` | `S1_llm_only` | `canonical_fact` | `caused_by` | thunderstorms | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ...OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-78d812053b4767d0` | `S1_llm_only` | `canonical_fact` | `will_follow_up_with` | updates if necessary | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-82a02dbdf01ea3db` | `S1_llm_only` | `canonical_fact` | `announces` | ORD airport arrival delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS |
| `cand-954223c6c8ab82ee` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 35 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS |
| `cand-b2f2b596fab11ce7` | `S1_llm_only` | `canonical_fact` | `applies_to_airspace_or_users` | ZAU users | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT |
| `cand-bc9276b0a02709f2` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T18:30:00 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-c0f518cb4c333e67` | `S1_llm_only` | `canonical_fact` | `maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES |
| `cand-c706c3c2b4726267` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T13:03:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO... |
| `cand-c73b910b3f3b9532` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T18:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-c86b55d842dd4a1a` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO... |
| `cand-d98d5011d5725bc8` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | O'Hare Airport | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ORD AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-e1b35f0ea45df78d` | `S1_llm_only` | `canonical_fact` | `can_expect` | airborne holding into O'Hare Airport up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-e3a4490d9c740f91` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | ZAU users can expect arrival delays / airborne holding into the O'Hare airport of up to 30 minutes due to thunderstorms. Updates will follow if necessary. | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-e42c83c71d659817` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T18:30:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO... |
| `cand-ed5be3908be8c64e` | `S1_llm_only` | `canonical_fact` | `effective_time_window` | 161303-161830 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161303-161830 |

## ATCSCC-GOLD-064 / 2026-05-19:112

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=112
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 32

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 192120-200230 SIGNATURE: 26/05/19 21:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-010ab42774bbf8fb` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-05a6f577a08157ea` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUT... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-11eed613d7076da2` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | DFW | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS /... |
| `cand-13ffe95ea458b2a6` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {"evidence_text": "DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT", "type": "nas:Airport"} | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT |
| `cand-1d974e8f4b2da93d` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZFW |
| `cand-1e94f9a93c4fe9ba` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-30e06911240494c4` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 112 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS /... |
| `cand-385bb1c9ea626c71` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUT... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-3ae00cb227cdedfa` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T21:20:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-4ac641321bd61580` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-4d6ce92e121bd728` | `S1_llm_only` | `canonical_fact` | `'has_advisory_title'}` | {'label': 'DFW Airport Arrival Delays'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS |
| `cand-54c1219971853847` | `S1_llm_only` | `canonical_fact` | `'extends_timeframe_of'}` | {'label': 'Advisory 039'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. |
| `cand-54e863e4b9f0b28f` | `S1_llm_only` | `canonical_fact` | `'maximum_delay_duration'}` | {'label': 'up to 30 minutes'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-61ffcd5f78004b8b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T21:20:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192120-200230 |
| `cand-665825838606905c` | `S1_llm_only` | `canonical_fact` | `'effective_time'}` | {'label': '192120-200230'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192120-200230 |
| `cand-6a506f9b00c90973` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 112 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-8b88d0c6e2408406` | `S1_llm_only` | `canonical_fact` | `'can_expect'}` | {'label': 'airborne holding'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-9287ba4ec9f9f0b0` | `S1_llm_only` | `canonical_fact` | `'caused_by'}` | {'label': 'thunderstorms'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-99c9633f3fbdacdb` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T21:21:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-9dbdb90f8e86f630` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-19T21:20:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-a380d84e290a5e71` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | thunderstorms | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-a3c10a2fd68bed7f` | `S1_llm_only` | `canonical_fact` | `'event_time_window'}` | {'label': '19/2100 - 20/0200'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/2100 - 20/0200 |
| `cand-a71aed38e80843f2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T21:20:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:20 |
| `cand-bc35e0a525acd656` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | weather | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS /... |
| `cand-c1f440b35c20bb63` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-c95c1f06670c56fa` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T21:21:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-cbd4698efcfd9a81` | `S1_llm_only` | `canonical_fact` | `'constrained_facility'}` | {'label': 'ZFW'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZFW |
| `cand-cd609d316645bd0a` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 112 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS |
| `cand-ce3395676511f54b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192120-200230 |
| `cand-d537b2f2ddb2134f` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {"evidence_text": "DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT", "type": "nas:Airport"} | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT |
| `cand-ed4cd0a3dbf58c77` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 112 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-fac8ec9190417fee` | `S1_llm_only` | `canonical_fact` | `'can_expect'}` | {'label': 'arrival delays'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |

## ATCSCC-GOLD-065 / 2026-05-16:061

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=61
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 40

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. CAPPING PLAN: KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 FOR APPROXIMATELY 300 MILES DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS. TUNNELING PLAN: FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE LINE OF THUNDERSTORMS. ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE S...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-072f75fe2ed2b830` | `S1_llm_only` | `canonical_fact` | `has_constrained_facility` | ZDV | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-0affc1d90b4455a1` | `S1_llm_only` | `canonical_fact` | `has_event_time` | 16/2115 - 17/0100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/2115 - 17/0100 |
| `cand-1a7e892230db8ac9` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | volume concerns in the high altitude sectors | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS. |
| `cand-1e079c39922a9e0b` | `S1_llm_only` | `canonical_fact` | `applies_for_distance` | approximately 300 miles | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FOR APPROXIMATELY 300 MILES |
| `cand-21698bd7cafe1a85` | `S1_llm_only` | `canonical_fact` | `may_be_necessary_due_to` | increased volume in the low altitude sectors | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE SECTORS. |
| `cand-3073229d66a06ee6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 61 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO B... |
| `cand-319b58394c2afd31` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T01:30:00 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 162039-170130 |
| `cand-344e58b2b81ed229` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T20:39:00 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 162039-170130 |
| `cand-3e879ddda288f043` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T20:39:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162039-170130 |
| `cand-3e9f2443040eea0a` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T20:39:00 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 20:39 |
| `cand-403e413245fa9a52` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | volume | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS |
| `cand-4901e1e2db74a1be` | `S1_llm_only` | `canonical_fact` | `may_be_descended_early` | earlier than normal | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY |
| `cand-525cce867f2daa63` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T01:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162039-170130 |
| `cand-54bb9cdb5256cb93` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:ARTCC(ZDV) | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-59c9f7a388566b0f` | `S1_llm_only` | `canonical_fact` | `is_expected_to` | build and impact the DEN terminal area | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. |
| `cand-5ce80aa43d206254` | `S1_llm_only` | `canonical_fact` | `causes` | volume concerns in the high altitude sectors | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS. |
| `cand-5d11566931b8bb00` | `S1_llm_only` | `canonical_fact` | `should_fuel_accordingly` | fuel accordingly | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FUEL ADVISORY: USERS SHOULD FUEL ACCORDINGLY. |
| `cand-611595db45480982` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | CAPPING PLAN: KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 FOR APPROXIMATELY 300 MILES DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VO... | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CAPPING PLAN: KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 FOR APPROXIMATELY 300 MILES DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS. |
| `cand-691080e838627c95` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | volume | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS |
| `cand-7a40e5945260f7c4` | `S1_llm_only` | `canonical_fact` | `may_be_capped` | AOB FL250 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 |
| `cand-7bfb27184f8e66e1` | `S1_llm_only` | `canonical_fact` | `causes` | volume concerns in the ZDV high altitude sectors | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE LINE OF THUNDERSTORMS. |
| `cand-812fa09efb898579` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | TUNNELING PLAN: FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE L... | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | TUNNELING PLAN: FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE LINE OF THUNDERSTORMS. |
| `cand-8c5dc858c0d482af` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 61 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 |
| `cand-8d3e523b4e3b2ab4` | `S1_llm_only` | `canonical_fact` | `is_for` | planning purposes only | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-9244af3ac42430a9` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI |
| `cand-aa3052def443c21d` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE SECTORS. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE SECTORS. |
| `cand-abcf26dd013b5eb5` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. |
| `cand-c266c83f609cd511` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-16T20:39:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 20:39 |
| `cand-c684cb6cb05bf943` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | volume concerns in the zdv high altitude sectors | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE LINE OF THUNDERSTORMS. |
| `cand-cc429bfa103f0fc9` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. |
| `cand-daf3928b01c9611a` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-e73168f3cecbb9e6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T01:30:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO B... |
| `cand-e9dae829f1ca2dc0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 61 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI |
| `cand-e9fb9545c73067e9` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport(DEN) | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | FLIGHTS INTO THE DEN AIRPORT |
| `cand-ef631a00306c1b42` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-16T20:39:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO B... |
| `cand-f43389e82fe70503` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T20:39:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO B... |
| `cand-f454e32bf3b226ea` | `S1_llm_only` | `canonical_fact` | `should_limit_requests_due_to` | increased volume and complexity in these sectors | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ADVISE FLIGHT CREWS TO LIMIT REQUESTS DUE TO INCREASED VOLUME AND COMPLEXITY IN THESE SECTORS. |
| `cand-f6fbcb83ac971026` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | PLEASE ADVISE FLIGHT CREWS TO LIMIT REQUESTS DUE TO INCREASED VOLUME AND COMPLEXITY IN THESE SECTORS. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PLEASE ADVISE FLIGHT CREWS TO LIMIT REQUESTS DUE TO INCREASED VOLUME AND COMPLEXITY IN THESE SECTORS. |
| `cand-f8eb7a6fadb147c4` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PU... | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO B... |
| `cand-fc6fb0fc9596919a` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport(KDEN) | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CAPPING PLAN: KDEN DEPARTURES |

## ATCSCC-GOLD-066 / 2026-05-17:011

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=11
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 20

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 170910 WSI DDS:170912 VA ADVISORY DTG: 20260517/0910Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0004 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/486 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. GEOPHYSICAL INST. ERUPTION DETAILS: PSBL VA EMS. EST VA DTG: 17/0830Z EST VA CLD: SFC/FL150 S0000 W07751 - S0004 W07739 - S0005 W07740 - S0004 W07752 - S0000 W07751 MOV W 10KT FCST VA CLD +6HR: 17/1430Z SFC/FL150 N0001 W07753 - S0004 W07739 - S0005 W07740 - S0003 W07755 - N0001 W07753 FCST VA CLD +12HR: 17/2030Z SFC/FL150 N0003 W07752 - S0004 W07739 - S0005 W07739 - S0001 W07755 - N0003 W07752 FCST...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0fa777bd22b3f646` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T17:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-2722862003169d87` | `S1_llm_only` | `canonical_fact` | `'reporting_action'}` | {'label': 'incr in seismic act near summit', 'type': 'activity_report'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | HWVR GEOPHYS INST RPRTD INCR IN SEISMIC ACT NEAR SUMMIT |
| `cand-286284c99ce66762` | `S1_llm_only` | `canonical_fact` | `'time_reference'}` | {'label': '17/0830Z', 'type': 'datetime_utc'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 17/0830Z |
| `cand-31fdf55ce2c258bc` | `S1_llm_only` | `canonical_fact` | `'forecast_prediction'}` | {'label': 'VA MOVG WNW', 'type': 'ash_movement'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDLS SUG ANY VA MOVG WNW |
| `cand-3707716e290b24d4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-4190533cd99f011f` | `S1_llm_only` | `canonical_fact` | `'attribute'}` | {'label': '11686 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-43b85fc2104d1ca9` | `S1_llm_only` | `canonical_fact` | `'inference'}` | {'label': 'volc act', 'type': 'volcanic_activity'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPLYING VOLC ACT. |
| `cand-48034da8ade7dd43` | `S1_llm_only` | `canonical_fact` | `'altitude_extent'}` | {'label': 'SFC/FL150', 'type': 'flight_level_range'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 |
| `cand-4a413d1d0becaf12` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-17T09:12:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 09:12 |
| `cand-518912306bd70276` | `S1_llm_only` | `canonical_fact` | `'activity_status'}` | {'label': 'PSBL VA EMS', 'type': 'event_description'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: PSBL VA EMS. |
| `cand-6291c14e2f19fbc0` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 11 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-8c78913c2a38f2c1` | `S1_llm_only` | `canonical_fact` | `'movement_description'}` | {'label': '10KT', 'type': 'speed'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV W 10KT |
| `cand-9bfed303b910e283` | `S1_llm_only` | `canonical_fact` | `'location_relation'}` | {'label': 'Ecuador', 'type': 'country'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-c0b5d7152edf88bd` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - REVENTADOR | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-c460acb566838886` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-17T09:10:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 09:12 |
| `cand-c5f1e5edcecd4745` | `S1_llm_only` | `canonical_fact` | `'forecast_prediction'}` | {'label': 'LTLCG', 'type': 'change_assessment'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WITH LTLCG FCST BY NWP MDLS. |
| `cand-cd8da35fd8cfdc55` | `S1_llm_only` | `canonical_fact` | `'observation_limitation'}` | {'label': 'volcanic ash not observed', 'type': 'observation_result'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO WX CLD CVR VA NOT OBSD BY EITHER WEBCAM OR STLT. |
| `cand-dd069a687c6d3546` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-e7f31ee05ffb5f19` | `S1_llm_only` | `canonical_fact` | `'describes_subject'}` | {'label': 'Reventador', 'type': 'volcano'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-f02bc74c55b2cd8b` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T17:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |

## ATCSCC-GOLD-067 / 2026-05-15:030

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=30
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA MESSAGE: FVXX22 KNES 151223 WSI DDS:151225 VA ADVISORY DTG: 20260515/1223Z VAAC: WASHINGTON VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS SOURCE ELEV: 4009 FT AMSL ADVISORY NR: 2026/026 INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. SOCIAL MEDIA. ERUPTION DETAILS: VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO VA EXP FCST VA CLD +18HR: 16/0600Z NO VA EXP RMK: RECENT VOL EPISODE CEASED AND VA DISPERSED. RESIDUAL VA MAY LINGER IN THE LOW LEVELS NEAR THE SUMMIT. SO2, WATER VAPOR AND OTHER GASES MAY EXTEND FURTHER. ...L...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04f373de3af1ffe0` | `S1_llm_only` | `canonical_fact` | `has_consequence` | volcanic ash dispersed | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RECENT VOL EPISODE CEASED AND VA DISPERSED. |
| `cand-0c6ea835bf22e2a3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-15a28fa17cb35343` | `S1_llm_only` | `canonical_fact` | `has_source_elevation` | 4009 ft AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 4009 FT AMSL |
| `cand-1834d603bd7c80cf` | `S1_llm_only` | `canonical_fact` | `is_located_in_area` | Hawaiian Islands | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: HAWAIIAN.IS |
| `cand-1d103e7cedf3c2f7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-15T12:23:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 12:25 |
| `cand-2243b4c7123eb473` | `S1_llm_only` | `canonical_fact` | `has_forecast_at_plus_6_hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/1800Z NO VA EXP |
| `cand-263030572632cccd` | `S1_llm_only` | `canonical_fact` | `may_linger_in` | the low levels near the summit | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESIDUAL VA MAY LINGER IN THE LOW LEVELS NEAR THE SUMMIT. |
| `cand-289261c9557b3975` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 30 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-367da914404ab3ec` | `S1_llm_only` | `canonical_fact` | `has_forecast_at_plus_18_hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/0600Z NO VA EXP |
| `cand-3fa856eed3ffa673` | `S1_llm_only` | `canonical_fact` | `has_advisory_number` | 2026/026 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/026 |
| `cand-51a34614b0ad548f` | `S1_llm_only` | `canonical_fact` | `was_observed_at_time` | 2026-05-15T12:01Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 15/1201Z |
| `cand-51a5b176a0e34715` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - KILAUEA | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-711767d27c32879b` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-15T12:25:00Z | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | SIGNATURE: 26/05/15 12:25 |
| `cand-79f73afc1c2ff0e5` | `S1_llm_only` | `canonical_fact` | `was_not_identifiable_from` | satellite data | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. |
| `cand-8916645326bf8584` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 30 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-915cec3637e890e4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-99b622462985ab3e` | `S1_llm_only` | `canonical_fact` | `may_extend_further_than` | residual volcanic ash | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SO2, WATER VAPOR AND OTHER GASES MAY EXTEND FURTHER. |
| `cand-a0748da08751ab43` | `S1_llm_only` | `canonical_fact` | `effective_time_window` | 150000-150000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a3771a1351d62d35` | `S1_llm_only` | `canonical_fact` | `has_forecast_at_plus_12_hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/0000Z NO VA EXP |
| `cand-a479102971cf6bca` | `S1_llm_only` | `canonical_fact` | `uses_information_sources` | GOES-18, HVO, Honolulu MWO, webcam, social media | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. SOCIAL MEDIA. |
| `cand-b073c0b5630e82ee` | `S1_llm_only` | `canonical_fact` | `has_eruption_status` | ended | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EMS ENDED. |
| `cand-b4a73320a1583393` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-b846b080926d07b0` | `S1_llm_only` | `canonical_fact` | `has_volcano_identifier` | 332010 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: KILAUEA 332010 |
| `cand-bb8c17c34ef25e7c` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T15:00:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-c12236cf2e5465f3` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO V... | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO VA EXP FCST VA CLD +18HR: 16/0600Z NO VA EX... |
| `cand-edaf08f398406d89` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 30 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/026 |
| `cand-f2f0bc571c94761b` | `S1_llm_only` | `canonical_fact` | `identifies_current_hazard_as` | volcanic activity bulletin for Kilauea | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |

## ATCSCC-GOLD-068 / 2026-05-18:126

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=126
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-07ad3c58c7e84222` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport(STL) | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT |
| `cand-0820a5058d36a750` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 18/2030Z - 19/0003Z |
| `cand-0a44c63a382383ee` | `S1_llm_only` | `canonical_fact` | `has_signature_timestamp` | 26/05/18 20:33 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:33 |
| `cand-0deddcdb76a2d35e` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | NONE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-12f24f4ddcd84477` | `S1_llm_only` | `canonical_fact` | `has_ground_stop_action` | GS CNX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-16d54005e27b215f` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T20:33:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/18 20:33 |
| `cand-198559a61fcc1846` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:33:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-1ba81f7ec784b7d2` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:33:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-2b25bcc1555e0368` | `S1_llm_only` | `canonical_fact` | `has_activity_time` | 2030Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-2be77d9a89e040fe` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | other | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-40a21f39721e0673` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-18T20:33:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:33 |
| `cand-450d3162700c797a` | `S1_llm_only` | `canonical_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-46e3be7f7401aa35` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T01:03:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-4dbc8c235de2f1de` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | nas:Airport(STL) | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT |
| `cand-50485eef76606d70` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 126 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX |
| `cand-59d01401c9835199` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-5df9d45722dc5cd5` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T01:03:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-655418d6fedf5993` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 18/2030Z - 19/0003Z |
| `cand-7dad81f38bd8c181` | `S1_llm_only` | `canonical_fact` | `names_control_element` | STL ELEMENT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-8797c5b2fab74412` | `S1_llm_only` | `canonical_fact` | `has_advisory_identifier` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX |
| `cand-8b33dafb74a2ea19` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 18/2030Z - 19/0003Z |
| `cand-8cb41f8ff998733b` | `S1_llm_only` | `canonical_fact` | `has_effective_time_range` | 182033-190103 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182033-190103 |
| `cand-99143c15a6c0787f` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 126 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 |
| `cand-a0e221613c4deb9f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-d8ce39d5c1ccc177` | `S1_llm_only` | `canonical_fact` | `has_operational_period` | 18/2030Z - 19/0003Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-f47f15ceeca0b97b` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | GS CNX PERIOD: 18/2030Z - 19/0003Z | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182033-190103 |
| `cand-f4d9617286cd213e` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |

## ATCSCC-GOLD-069 / 2026-05-20:192

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=192
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 20

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 192 PHL/ZNY 05/20/2026 CDM GS CNX MESSAGE: CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1a7758f9835de490` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 192 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 192 PHL/ZNY 05/20/2026 CDM GS CNX |
| `cand-1ada831ea280a15a` | `S1_llm_only` | `canonical_fact` | `has_controlled_element` | PHL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-35472c9210cc4174` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | nas:Airport/PHL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-4ad6c48300bf8761` | `S1_llm_only` | `canonical_fact` | `was_signed_at` | 26/05/20 23:47 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 23:47 |
| `cand-6a363a3cc5a0deb7` | `S1_llm_only` | `canonical_fact` | `has_applicability_period` | 20/2345Z - 21/0145Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 20/2345Z - 21/0145Z |
| `cand-7720fed320a23a15` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-7ad7af837b4ca1a0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T23:47:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 23:47 |
| `cand-7c0a88f2de4f40af` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-84f361cfd3b38173` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PHL | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL |
| `cand-91c568411f2a0b79` | `S1_llm_only` | `canonical_fact` | `announces_ground_stop_cancellation` | GS CNX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-9dc0e60563e106b9` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | GS CNX | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-a479aed928cd4a52` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | PHL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-a6180949579f4769` | `S1_llm_only` | `canonical_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-a772c155996d6a40` | `S1_llm_only` | `canonical_fact` | `has_advisory_time` | 2345Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2345Z |
| `cand-ad37ee9e206e506f` | `S1_llm_only` | `canonical_fact` | `references_air_traffic_control_system_command_center` | ATCSCC Advisory | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC Advisory |
| `cand-afb28de6788ff6de` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T23:47:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202347-210245 |
| `cand-dca57f31d989aeb4` | `S1_llm_only` | `canonical_fact` | `has_effective_time_range` | 202347-210245 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202347-210245 |
| `cand-de35591f1fed10d7` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T23:45:00Z | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-deec7d63dba45a99` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202347-210245 |
| `cand-ff01592b21bedb8f` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T01:45:00Z | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |

## ATCSCC-GOLD-070 / 2026-05-14:014

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=14
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 140155 WSI DDS:140157 VA ADVISORY DTG: 20260514/0155Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/559 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: LIKELY VA EMS EST VA DTG: 14/0130Z EST VA CLD: SFC/FL150 N1429 W09101 - N1429 W09052 - N1428 W09052 - N1421 W09058 - N1429 W09101 MOV SW 10KT FCST VA CLD +6HR: 14/0730Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1411 W09055 - N1416 W09104 - N1429 W09053 FCST VA CLD +12HR: 14/1330Z SFC/FL150 N1429 W09052 - N1428 W09052 - N1415 W09100 - N1421 W09106 - N1429 W09052 FCST VA CLD +18HR: 14/1930Z...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0f021019706807ae` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-0fcb9fa336229a04` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 14 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-1c1ad3921bd6942e` | `S1_llm_only` | `canonical_fact` | `'were not observed on satellite or webcam due to weather clouds'}` | {'label': 'weather clouds', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS NOT OBS ON STLT OR WEBCAM DUE TO WX CLDS |
| `cand-2fc49771b69de671` | `S1_llm_only` | `canonical_fact` | `'source elevation is'}` | {'label': '12346 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-327ffda00881fd72` | `S1_llm_only` | `canonical_fact` | `'has bulletin subject'}` | {'label': 'Fuego volcanic activity bulletin', 'type': 'bulletin'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-6bc02ef3115709d1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-14T01:55:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 01:57 |
| `cand-7467cef155e37bd8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-861692578054d72d` | `S1_llm_only` | `canonical_fact` | `'forecast position time plus 18 hours is'}` | {'label': '14/1930Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 14/1930Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1415 W09058 - N1420 W09104 - N1429 W09053 |
| `cand-8a4b4125cdbff34c` | `S1_llm_only` | `canonical_fact` | `'eruption activity is assessed as'}` | {'label': 'likely volcanic ash emissions', 'type': 'eruption_assessment'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: LIKELY VA EMS |
| `cand-8d3dca3fc5b9c1ef` | `S1_llm_only` | `canonical_fact` | `'forecast position time plus 6 hours is'}` | {'label': '14/0730Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/0730Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1411 W09055 - N1416 W09104 - N1429 W09053 |
| `cand-99b15c7755d1d509` | `S1_llm_only` | `canonical_fact` | `'continue'}` | {'label': 'continue', 'type': 'activity_state'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BUT EMS LIKELY TO CONT. |
| `cand-a70de516b528ae25` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T01:57:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 01:57 |
| `cand-aa3cc98cba681258` | `S1_llm_only` | `canonical_fact` | `'is moving'}` | {'label': 'SW at 10KT', 'type': 'movement'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-c377188a19b6d63a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-c3e7d2a804174d45` | `S1_llm_only` | `canonical_fact` | `'estimated position time is'}` | {'label': '14/0130Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 14/0130Z |
| `cand-c54e315698aa97ba` | `S1_llm_only` | `canonical_fact` | `'is expected through'}` | {'label': 'T+18', 'type': 'forecast_horizon'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GEN SW MVMT EXP THRU T+18 ACCORDING TO NWP MDLS |
| `cand-efedfc1aaccb0c00` | `S1_llm_only` | `canonical_fact` | `'estimated vertical extent is'}` | {'label': 'SFC/FL150', 'type': 'altitude_range'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 N1429 W09101 - N1429 W09052 - N1428 W09052 - N1421 W09058 - N1429 W09101 |
| `cand-f96dcdab8e2b50dd` | `S1_llm_only` | `canonical_fact` | `'is located in'}` | {'label': 'Guatemala', 'type': 'country_or_region'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-fb9773855c2f715c` | `S1_llm_only` | `canonical_fact` | `'forecast position time plus 12 hours is'}` | {'label': '14/1330Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/1330Z SFC/FL150 N1429 W09052 - N1428 W09052 - N1415 W09100 - N1421 W09106 - N1429 W09052 |
