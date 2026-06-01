# NASA ATMONTO Gold Review batch_07

- Samples: `ATCSCC-GOLD-061` to `ATCSCC-GOLD-070`
- Records: 10
- Candidate clusters: 210

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-061 / 2026-05-15:017

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=17
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA MESSAGE: FVXX22 KNES 150845 WSI DDS:150847 VA ADVISORY DTG: 20260515/0845Z VAAC: WASHINGTON VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS SOURCE ELEV: 4009 FT AMSL ADVISORY NR: 2026/025 INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. NWP MODELS. ERUPTION DETAILS: ERUPTION CONTINUES OBS VA DTG: 15/0826Z OBS VA CLD: SFC/FL100 N1931 W15526 - N1926 W15517 - N1924 W15516 - N1921 W15532 - N1931 W15526 MOV W 10KT SFC/FL200 N2013 W15354 - N2002 W15347 - N1940 W15435 - N1946 W15444 - N2013 W15354 MOV NE 20KT FCST VA CLD +6HR: 15/1430Z SFC/FL100 N1943 W15534 - N1926 W15516 - N1924 W15516 - N1907 W15543 - N1943 W15534 SFC/FL200 NO VA...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-006142b4145cf1dc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was moving` | west at 10 kt | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV W 10KT |
| `cand-0908a0cc8087e49a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was moving` | northeast at 20 kt | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 20KT |
| `cand-10ecdf9a6da7015f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expected ash presence` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/0230Z NO VA EXP |
| `cand-16808371f4006636` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is in area` | Hawaiian Islands | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: HAWAIIAN.IS |
| `cand-1b579ebda46c6f72` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is expected` | northwest movement | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NW MVMT EXP AT FL100 BY T+6 |
| `cand-35b4e55827c2a6bf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed vertical extent` | surface to FL100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL100 |
| `cand-3d61e9efb6abd0fb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is expected to dissipate by` | T+6 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXP TO DISSIPATE BY T+6 |
| `cand-4445d6f5922ea69d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `were dispersing` | toward the southwest farther from summit | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISPERSING TWD THE SW FURTHER FM SUMMIT |
| `cand-46c791d92a7a4e64` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expected no ash above` | FL200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SFC/FL200 NO VA EXP |
| `cand-4df0774143fcf4cc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is possible` | southwest dispersion | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WITH DISPERSION SW PSBL |
| `cand-5a3e23120632ab6a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `were moving` | west-northwest from summit | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVG WNW FM SUMMIT |
| `cand-5cd72854c0adaad1` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 17 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-678de388f35addc0` | `S2_llm_schema_slice` | `property_bundle` | `controlledNASelement` | {"atm:controlledNASelement": [{"evidence_text": "VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS", "value": {"class": "nas:Airport", "label": "Ki... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-6d547947d82f731f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `were observed on satellite` | observed on satellite | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBS ON STLT |
| `cand-7b2390101dafa4ba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is continuing` | continuing | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ERUPTION CONTINUES |
| `cand-7e46d3505b2449e6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has elevation` | 4009 ft AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 4009 FT AMSL |
| `cand-8acdbc267e9e1b5c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `observed vertical extent` | surface to FL200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SFC/FL200 |
| `cand-9217f8a1d677cfef` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may be obscured by` | weather clouds | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FURTHER EMS MAY BE OBSC BY WX CLDS |
| `cand-98eb9cb4e7151070` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was observed` | off coast northeast from summit | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMNANT LGT VA CLD AT FL200 OBS OFF COAST NE FM SUMMIT |
| `cand-9adfb621c3966e0e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expected vertical extent` | surface to FL100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/1430Z SFC/FL100 |
| `cand-a30c76196fcd7425` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T08:45:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 08:47 |
| `cand-b07527be8caa1f90` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA", "value": 17}], "atm:effectiveEndTime": [{"e... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-b8cf6dd6a3a6beab` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is the volcano named in the advisory` | Kilauea | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: KILAUEA |
| `cand-bad560966574e174` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expected ash presence` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/2030Z NO VA EXP |
| `cand-bb259b85a74406bf` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-e44b1b51712a5062` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |

## ATCSCC-GOLD-062 / 2026-05-20:029

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=29
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 200210 CCA WSI DDS:200212 VA ADVISORY -CORRECTION DTG: 20260520/0210Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/585 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 20/0140Z EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 MOV SW 10KT FCST VA CLD +6HR: 20/0730Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 FCST VA CLD +18HR:...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0d4f29b385e374b5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecasts no change in model winds'}` | {'label': 'next 18 hours', 'text': 'NXT 18 HR'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-1baddca7065e9ef4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast valid at'}` | {'label': '2026-05-20 19:30Z', 'text': '20/1930Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/1930Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09052 |
| `cand-277946f0e4836ee9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast valid at'}` | {'label': '2026-05-20 13:30Z', 'text': '20/1330Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 |
| `cand-2fd0f77fd8b52da2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'moves toward'}` | {'label': 'southwest', 'text': 'MOV SW 10KT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-31fa5dbfaa7b3cb3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is located in'}` | {'label': 'Guatemala', 'text': 'AREA: GUATEMALA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-61c59d6a3f43d957` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports detection status'}` | {'label': 'not detected on satellite', 'text': 'VA NOT DETECTED ON STLT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-61f37e6fc19d16f7` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-20T02:12:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 02:12 |
| `cand-675e9950c2cc166f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has speed'}` | {'label': '10 knots', 'text': 'MOV SW 10KT'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-6f2da8a22484398d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has vertical extent'}` | {'label': 'surface to flight level 140', 'text': 'SFC/FL140'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 |
| `cand-784fb84c0dad43c6` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 29 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-79d10aefbd3fde91` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-9515fdf4535e5921` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has correction timestamp'}` | {'label': '2026-05-20 02:10Z', 'text': 'DTG: 20260520/0210Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY -CORRECTION DTG: 20260520/0210Z |
| `cand-a3c84d3424893ae1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces bulletin about'}` | {'label': 'volcanic activity bulletin for Fuego', 'text': 'VOLCANIC ACTIVITY BULLETIN - FUEGO'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-a951d3b444750dc2` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T02:10:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 02:12 |
| `cand-b15abc5f589c325d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has source elevation'}` | {'label': '12346 ft amsl', 'text': 'SOURCE ELEV: 12346 FT AMSL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-cd48dfd47ca73414` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-20T20:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-cf4fc6a6fe47192a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'gives reason'}` | {'label': 'weather clouds in summit area', 'text': 'WX CLDS IN SUMMIT AREA'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-d38d75e0e0d0db40` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'predicts continued emissions'}` | {'label': 'likely continue', 'text': 'LIKELY CONTINUE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-d43929b72202c83a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states eruption status'}` | {'label': 'ongoing', 'text': 'ONGOING'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING |
| `cand-d8e2395b9aaae10c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast valid at'}` | {'label': '2026-05-20 07:30Z', 'text': '20/0730Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/0730Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 |
| `cand-d92fa552f8a73a89` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 29 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-d9805d04f40d483b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated start time'}` | {'label': '2026-05-20 01:40Z', 'text': '20/0140Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS EST VA DTG: 20/0140Z |
| `cand-dcd6418d5929c5e2` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-f37483e3982c7d50` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-fc81de610a47f111` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |

## ATCSCC-GOLD-063 / 2026-05-16:035

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=35
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 16

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 161303-161830 SIGNATURE: 26/05/16 13:03 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1388d5505f2fcd09` | `S1_llm_only` | `freeform_or_unmapped_fact` | `event_time_window` | 16/1300 - 16/1800 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1300 - 16/1800 |
| `cand-207f4906ada6986f` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T13:03:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 13:03 |
| `cand-21c227601d4bcab0` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"name": "O'Hare Airport", "type": "nas:Airport"}, "atm:extensionProbability": "NONE", "atm:impactingCondition": "weather"} | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ORD AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-4fa414e577ab2621` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time_window` | 161303-161830 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161303-161830 |
| `cand-6038489c7d015554` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T13:03:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-78411563be62b0ba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_to_airspace_or_users` | ZAU users | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT |
| `cand-92e45c5cc0f006b4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `maximum_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES |
| `cand-954223c6c8ab82ee` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 35 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS |
| `cand-9803fee666a06557` | `S1_llm_only` | `freeform_or_unmapped_fact` | `caused_by` | thunderstorms | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ...OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-9b4fbbb29308c9a8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect` | airborne holding into O'Hare Airport up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-c73b910b3f3b9532` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T18:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-de05a23c41294e16` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 35, "atm:effectiveEndTime": "2026-05-16T18:30:00", "atm:effectiveStartTime": "2026-05-16T13:03:00", "atm:initiativeComments": "ZAU USE... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO... |
| `cand-e2dd2eeb5538ced7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `will_follow_up_with` | updates if necessary | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-e5ef08be9b6ee87f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces` | ORD airport arrival delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS |
| `cand-ed3ba67fc3497907` | `S1_llm_only` | `freeform_or_unmapped_fact` | `can_expect` | arrival delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-f13cc03b429a7cd9` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS", "value": 35}], "atm:effectiveEndTime": [{"evidenc... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |

## ATCSCC-GOLD-064 / 2026-05-19:112

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=112
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 16

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 192120-200230 SIGNATURE: 26/05/19 21:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0854081ced0da3d9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'caused_by'}` | {'label': 'thunderstorms'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-0af49040072854a5` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 112, "atm:controlledNASelement": {"evidence_text": "DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT", "type": "nas:... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-0b676862898a2029` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'constrained_facility'}` | {'label': 'ZFW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZFW |
| `cand-1a0e272ebc7a48b7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'event_time_window'}` | {'label': '19/2100 - 20/0200'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/2100 - 20/0200 |
| `cand-4ab5297e0ba0bf37` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'effective_time'}` | {'label': '192120-200230'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192120-200230 |
| `cand-56c22f184ddfa629` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_advisory_title'}` | {'label': 'DFW Airport Arrival Delays'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS |
| `cand-5d97ca786d07caab` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'extends_timeframe_of'}` | {'label': 'Advisory 039'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. |
| `cand-61ffcd5f78004b8b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T21:20:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192120-200230 |
| `cand-6d31cc466e8cc7b8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'can_expect'}` | {'label': 'airborne holding'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-7449ae0204e22403` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 112 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS /... |
| `cand-7a33cd2f12601dcc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'can_expect'}` | {'label': 'arrival delays'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-9d8c0f23b7e80afa` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 112, "atm:controlledNASelement": {"evidence_text": "DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT", "type": "nas:... | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USER... |
| `cand-a71aed38e80843f2` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T21:20:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:20 |
| `cand-cd609d316645bd0a` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 112 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS |
| `cand-ce3395676511f54b` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192120-200230 |
| `cand-d15298a6e6d3c1ae` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'maximum_delay_duration'}` | {'label': 'up to 30 minutes'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |

## ATCSCC-GOLD-065 / 2026-05-16:061

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=61
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. CAPPING PLAN: KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 FOR APPROXIMATELY 300 MILES DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS. TUNNELING PLAN: FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE LINE OF THUNDERSTORMS. ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE S...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-132b7af5bf29b64e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_event_time` | 16/2115 - 17/0100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/2115 - 17/0100 |
| `cand-18cea4ef7f020397` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_be_descended_early` | earlier than normal | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY |
| `cand-1a2d0155ed126f9a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_facility` | ZDV | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-1d04596ca418a93a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_be_capped` | AOB FL250 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 |
| `cand-1fe49cd4d9bafd06` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_be_necessary_due_to` | increased volume in the low altitude sectors | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE SECTORS. |
| `cand-24f51da473cb1266` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport(KDEN) | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CAPPING PLAN: KDEN DEPARTURES |
| `cand-3147c1c8ae0969c2` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | volume | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS |
| `cand-315bf2b3bcb1718b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport(DEN) | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | FLIGHTS INTO THE DEN AIRPORT |
| `cand-3375401773f2294f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:ARTCC(ZDV) | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-351f11c4375ac636` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | FYI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI |
| `cand-3d37de19491c4ece` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-17T01:30:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 162039-170130 |
| `cand-3e879ddda288f043` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T20:39:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162039-170130 |
| `cand-4c054679107c2d05` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. |
| `cand-525cce867f2daa63` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T01:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162039-170130 |
| `cand-542cc2ee6863da72` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_for` | planning purposes only | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-6dea2b33e2871477` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_expected_to` | build and impact the DEN terminal area | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. |
| `cand-b061762cd940bbaf` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | TUNNELING PLAN: FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE L... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | TUNNELING PLAN: FLIGHTS INTO THE DEN AIRPORT FROM THE EAST MAY BE DESCENDED EARLY DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE LINE OF THUNDERSTORMS. |
| `cand-b17d649fdf20331d` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | CAPPING PLAN: KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 FOR APPROXIMATELY 300 MILES DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VO... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CAPPING PLAN: KDEN DEPARTURES TO THE NORTH / EAST / SOUTH MAY BE CAPPED AOB FL250 FOR APPROXIMATELY 300 MILES DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS. |
| `cand-b4d7218a14551bf0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should_limit_requests_due_to` | increased volume and complexity in these sectors | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ADVISE FLIGHT CREWS TO LIMIT REQUESTS DUE TO INCREASED VOLUME AND COMPLEXITY IN THESE SECTORS. |
| `cand-b4ff3f95d91616d9` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE SECTORS. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ADDITIONAL TMI'S MAY BE NECESSARY DUE TO INCREASED VOLUME IN THE LOW ALTITUDE SECTORS. |
| `cand-b79f345ccc8846a8` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO BUILD AND IMPACT THE DEN TERMINAL AREA. |
| `cand-c18288be644b1571` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_for_distance` | approximately 300 miles | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FOR APPROXIMATELY 300 MILES |
| `cand-c266c83f609cd511` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-16T20:39:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 20:39 |
| `cand-c413422715b12d1d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should_fuel_accordingly` | fuel accordingly | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FUEL ADVISORY: USERS SHOULD FUEL ACCORDINGLY. |
| `cand-c73f5c177ee143aa` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 61 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 |
| `cand-c8b243da1964ce75` | `S1_llm_only` | `freeform_or_unmapped_fact` | `causes` | volume concerns in the high altitude sectors | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO A LARGE AREA OF THUNDERSTORMS CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS. |
| `cand-ccd0f2c7a21d1fc1` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-16T20:39:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 162039-170130 |
| `cand-deacdc809851da43` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 61 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI MESSAGE: EVENT TIME: 16/2115 - 17/0100 CONSTRAINED FACILITIES: ZDV THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. WIDELY SCATTERED SHRA & TSRA AREA EXPECTED TO B... |
| `cand-e0ec76741b835c15` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-16T20:39:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 20:39 |
| `cand-e191de3b4c9f74a4` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | volume | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CAUSING VOLUME CONCERNS IN THE HIGH ALTITUDE SECTORS |
| `cand-e986fd886eb201c6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `causes` | volume concerns in the ZDV high altitude sectors | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO VOLUME CONCERNS IN THE ZDV HIGH ALTITUDE SECTORS CAUSED BY A LARGE LINE OF THUNDERSTORMS. |
| `cand-e9dae829f1ca2dc0` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 61 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI |
| `cand-f920d9d1013e8d0b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | PLEASE ADVISE FLIGHT CREWS TO LIMIT REQUESTS DUE TO INCREASED VOLUME AND COMPLEXITY IN THESE SECTORS. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PLEASE ADVISE FLIGHT CREWS TO LIMIT REQUESTS DUE TO INCREASED VOLUME AND COMPLEXITY IN THESE SECTORS. |

## ATCSCC-GOLD-066 / 2026-05-17:011

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=11
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 170910 WSI DDS:170912 VA ADVISORY DTG: 20260517/0910Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0004 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/486 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. GEOPHYSICAL INST. ERUPTION DETAILS: PSBL VA EMS. EST VA DTG: 17/0830Z EST VA CLD: SFC/FL150 S0000 W07751 - S0004 W07739 - S0005 W07740 - S0004 W07752 - S0000 W07751 MOV W 10KT FCST VA CLD +6HR: 17/1430Z SFC/FL150 N0001 W07753 - S0004 W07739 - S0005 W07740 - S0003 W07755 - N0001 W07753 FCST VA CLD +12HR: 17/2030Z SFC/FL150 N0003 W07752 - S0004 W07739 - S0005 W07739 - S0001 W07755 - N0003 W07752 FCST...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1c7d651b4dd98303` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'location_relation'}` | {'label': 'Ecuador', 'type': 'country'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-2afa595fe0f955a7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'activity_status'}` | {'label': 'PSBL VA EMS', 'type': 'event_description'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: PSBL VA EMS. |
| `cand-3707716e290b24d4` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-3726a99353541077` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'describes_subject'}` | {'label': 'Reventador', 'type': 'volcano'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-38fd4dbf7566d6e2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_prediction'}` | {'label': 'VA MOVG WNW', 'type': 'ash_movement'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDLS SUG ANY VA MOVG WNW |
| `cand-4edf816c312e281c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reporting_action'}` | {'label': 'incr in seismic act near summit', 'type': 'activity_report'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | HWVR GEOPHYS INST RPRTD INCR IN SEISMIC ACT NEAR SUMMIT |
| `cand-6291c14e2f19fbc0` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 11 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-81165c6ef5a6a2ee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'inference'}` | {'label': 'volc act', 'type': 'volcanic_activity'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPLYING VOLC ACT. |
| `cand-8841efe79e4a6941` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'movement_description'}` | {'label': '10KT', 'type': 'speed'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV W 10KT |
| `cand-a222db5eb074cde0` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR", "value": 11}], "atm:effectiveEndTime": [... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-a2c4da41dfa335f8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'time_reference'}` | {'label': '17/0830Z', 'type': 'datetime_utc'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 17/0830Z |
| `cand-b00a7cedb5ec115e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'altitude_extent'}` | {'label': 'SFC/FL150', 'type': 'flight_level_range'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 |
| `cand-bfbb9f58b6ccb147` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'attribute'}` | {'label': '11686 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-c460acb566838886` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T09:10:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 09:12 |
| `cand-d84b23d633d2b8e9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'observation_limitation'}` | {'label': 'volcanic ash not observed', 'type': 'observation_result'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO WX CLD CVR VA NOT OBSD BY EITHER WEBCAM OR STLT. |
| `cand-dd069a687c6d3546` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-e6369c23d25c0693` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast_prediction'}` | {'label': 'LTLCG', 'type': 'change_assessment'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WITH LTLCG FCST BY NWP MDLS. |

## ATCSCC-GOLD-067 / 2026-05-15:030

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=30
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA MESSAGE: FVXX22 KNES 151223 WSI DDS:151225 VA ADVISORY DTG: 20260515/1223Z VAAC: WASHINGTON VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS SOURCE ELEV: 4009 FT AMSL ADVISORY NR: 2026/026 INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. SOCIAL MEDIA. ERUPTION DETAILS: VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO VA EXP FCST VA CLD +18HR: 16/0600Z NO VA EXP RMK: RECENT VOL EPISODE CEASED AND VA DISPERSED. RESIDUAL VA MAY LINGER IN THE LOW LEVELS NEAR THE SUMMIT. SO2, WATER VAPOR AND OTHER GASES MAY EXTEND FURTHER. ...L...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0f4cb367a0c572d4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_number` | 2026/026 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/026 |
| `cand-1d103e7cedf3c2f7` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T12:23:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 12:25 |
| `cand-1e89774f2ea6c5ba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_eruption_status` | ended | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EMS ENDED. |
| `cand-289261c9557b3975` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 30 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-2932b2cea31ae29d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_consequence` | volcanic ash dispersed | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RECENT VOL EPISODE CEASED AND VA DISPERSED. |
| `cand-2d062b8d9169c920` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_volcano_identifier` | 332010 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: KILAUEA 332010 |
| `cand-2f30a564796b5e4f` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - KILAUEA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-4550efd128e3ee91` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_current_hazard_as` | volcanic activity bulletin for Kilauea | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-591253051370eaa3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_forecast_at_plus_12_hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/0000Z NO VA EXP |
| `cand-6203b27ace878c0b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_source_elevation` | 4009 ft AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 4009 FT AMSL |
| `cand-6a705c862d91b9dc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was_observed_at_time` | 2026-05-15T12:01Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 15/1201Z |
| `cand-77c74435a9f35ce8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was_not_identifiable_from` | satellite data | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. |
| `cand-7d0ff744b00430d4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_forecast_at_plus_6_hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/1800Z NO VA EXP |
| `cand-880d50232eb3a6f6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time_window` | 150000-150000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-8f7f8992e67c7ce7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_located_in_area` | Hawaiian Islands | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: HAWAIIAN.IS |
| `cand-915cec3637e890e4` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-9e0291d92e6cb599` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_extend_further_than` | residual volcanic ash | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SO2, WATER VAPOR AND OTHER GASES MAY EXTEND FURTHER. |
| `cand-a523e2fe19394c9c` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-15T15:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-ac6c9f6cc8d8c2a6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `may_linger_in` | the low levels near the summit | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESIDUAL VA MAY LINGER IN THE LOW LEVELS NEAR THE SUMMIT. |
| `cand-af8330577cc54d09` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO V... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO VA EXP FCST VA CLD +18HR: 16/0600Z NO VA EX... |
| `cand-b4a73320a1583393` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-db4725f03550da73` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 30 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-e1ac5b0e9ca307cb` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-15T12:25:00Z | `{"rejected_schema": 2}` | `{"unknown_fact_type": 2, "unknown_subject_class": 2}` | SIGNATURE: 26/05/15 12:25 |
| `cand-e850d6503210742f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `uses_information_sources` | GOES-18, HVO, Honolulu MWO, webcam, social media | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. SOCIAL MEDIA. |
| `cand-f44b02b883a99898` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-fec3769f8e8951ba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_forecast_at_plus_18_hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/0600Z NO VA EXP |

## ATCSCC-GOLD-068 / 2026-05-18:126

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=126
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-16d54005e27b215f` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T20:33:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:33 |
| `cand-198559a61fcc1846` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:33:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-1def3911e31e0159` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_operational_period` | 18/2030Z - 19/0003Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-36ddfa73d625f5c1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_activity_time` | 2030Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-50485eef76606d70` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 126 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX |
| `cand-59d01401c9835199` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-5df9d45722dc5cd5` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T01:03:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-726b228915d6b1f1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-78592ad49c630025` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_identifier` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX |
| `cand-8afeca3f4faebb1f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_ground_stop_action` | GS CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-a0e221613c4deb9f` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-aa62e848129395e6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_signature_timestamp` | 26/05/18 20:33 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:33 |
| `cand-b23c0a54820d4e02` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time_range` | 182033-190103 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182033-190103 |
| `cand-b5a497132bf181bd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_control_element` | STL ELEMENT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-da662238939f4c5b` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": {"evidence_text": "ATCSCC ADVZY 126 STL/ZKC 05/18/2026", "value": 126}, "atm:controlledNASelement": {"evidence_text": "CTL ELEMENT: ST... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 |
| `cand-e2d5435d19bf7f22` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: STL ELEMENT TYPE: APT", "value": "nas:Airport(STL)"}], "atm:effectiveEndTime": [{"evidence_text... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-febd08af4e101d1d` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"evidence_text": "CTL ELEMENT: STL ELEMENT TYPE: APT", "value": "nas:Airport(STL)"}, "atm:extensionProbability": {"evidence_tex... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 |

## ATCSCC-GOLD-069 / 2026-05-20:192

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=192
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 16

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 192 PHL/ZNY 05/20/2026 CDM GS CNX MESSAGE: CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05288b6bf306a241` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces_ground_stop_cancellation` | GS CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-139fa43945e61351` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_applicability_period` | 20/2345Z - 21/0145Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 20/2345Z - 21/0145Z |
| `cand-1a7758f9835de490` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 192 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 192 PHL/ZNY 05/20/2026 CDM GS CNX |
| `cand-2fb22a63cd88b1f0` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport/PHL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-343423385ad4df98` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_time` | 2345Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2345Z |
| `cand-388a0c3c1efb2003` | `S1_llm_only` | `freeform_or_unmapped_fact` | `references_air_traffic_control_system_command_center` | ATCSCC Advisory | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC Advisory |
| `cand-3a755dc8cec4efce` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": "PHL", "atm:effectiveEndTime": "2026-05-21T01:45:00Z", "atm:effectiveStartTime": "2026-05-20T23:45:00Z", "atm:implementationStat... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-448770e9fa36b22a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was_signed_at` | 26/05/20 23:47 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 23:47 |
| `cand-7720fed320a23a15` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-7ad7af837b4ca1a0` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T23:47:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 23:47 |
| `cand-84f361cfd3b38173` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PHL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL |
| `cand-afb28de6788ff6de` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T23:47:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202347-210245 |
| `cand-c4b3fd4164658236` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time_range` | 202347-210245 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202347-210245 |
| `cand-cf3864f423db1c07` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_controlled_element` | PHL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-d899c876fc061af7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-deec7d63dba45a99` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:45:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202347-210245 |

## ATCSCC-GOLD-070 / 2026-05-14:014

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=14
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 18

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 140155 WSI DDS:140157 VA ADVISORY DTG: 20260514/0155Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/559 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: LIKELY VA EMS EST VA DTG: 14/0130Z EST VA CLD: SFC/FL150 N1429 W09101 - N1429 W09052 - N1428 W09052 - N1421 W09058 - N1429 W09101 MOV SW 10KT FCST VA CLD +6HR: 14/0730Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1411 W09055 - N1416 W09104 - N1429 W09053 FCST VA CLD +12HR: 14/1330Z SFC/FL150 N1429 W09052 - N1428 W09052 - N1415 W09100 - N1421 W09106 - N1429 W09052 FCST VA CLD +18HR: 14/1930Z...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0fcb9fa336229a04` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 14 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-216bc09767beb03c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is moving'}` | {'label': 'SW at 10KT', 'type': 'movement'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-21c3467a29b74442` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'were not observed on satellite or webcam due to weather clouds'}` | {'label': 'weather clouds', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS NOT OBS ON STLT OR WEBCAM DUE TO WX CLDS |
| `cand-2f5bfe482db23e2b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated vertical extent is'}` | {'label': 'SFC/FL150', 'type': 'altitude_range'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 N1429 W09101 - N1429 W09052 - N1428 W09052 - N1421 W09058 - N1429 W09101 |
| `cand-379c2d02ccb3206c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is located in'}` | {'label': 'Guatemala', 'type': 'country_or_region'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-57a50d3cea29e91c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'source elevation is'}` | {'label': '12346 FT AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-6bc02ef3115709d1` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T01:55:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 01:57 |
| `cand-7467cef155e37bd8` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-805841bed5f5f5d4` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO", "value": 14}], "atm:initiativeComments": [{"e... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-a5ba84cb85ad37dd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated position time is'}` | {'label': '14/0130Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 14/0130Z |
| `cand-c377188a19b6d63a` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-cd05ef2cd483597f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has bulletin subject'}` | {'label': 'Fuego volcanic activity bulletin', 'type': 'bulletin'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-d28020ae3ef18b7a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast position time plus 18 hours is'}` | {'label': '14/1930Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 14/1930Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1415 W09058 - N1420 W09104 - N1429 W09053 |
| `cand-eb20bb5810225103` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast position time plus 6 hours is'}` | {'label': '14/0730Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/0730Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1411 W09055 - N1416 W09104 - N1429 W09053 |
| `cand-ec8d3bf9a19ddbe9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'forecast position time plus 12 hours is'}` | {'label': '14/1330Z', 'type': 'time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/1330Z SFC/FL150 N1429 W09052 - N1428 W09052 - N1415 W09100 - N1421 W09106 - N1429 W09052 |
| `cand-f16c925fd543aa93` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is expected through'}` | {'label': 'T+18', 'type': 'forecast_horizon'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GEN SW MVMT EXP THRU T+18 ACCORDING TO NWP MDLS |
| `cand-f3cf17d2d1ed7631` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'eruption activity is assessed as'}` | {'label': 'likely volcanic ash emissions', 'type': 'eruption_assessment'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: LIKELY VA EMS |
| `cand-f8d5012c4e9b181f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'continue'}` | {'label': 'continue', 'type': 'activity_state'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BUT EMS LIKELY TO CONT. |
