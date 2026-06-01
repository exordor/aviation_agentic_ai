# NASA ATMONTO Gold Review batch_06

- Samples: `ATCSCC-GOLD-051` to `ATCSCC-GOLD-060`
- Records: 10
- Candidate clusters: 247

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-051 / 2026-05-14:030

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=30
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 22

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA MESSAGE: FVXX21 KNES 140834 WSI DDS:140836 VA ADVISORY DTG: 20260514/0834Z VAAC: WASHINGTON VOLCANO: SANTA MARIA 342030 PSN: N1445 W09133 AREA: GUATEMALA SOURCE ELEV: 12287 FT AMSL ADVISORY NR: 2026/237 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: LGT VA EMS OBS VA DTG: 14/0800Z OBS VA CLD: SFC/FL140 N1446 W09133 - N1444 W09132 - N1437 W09139 - N1442 W09144 - N1446 W09133 MOV SW 5KT FCST VA CLD +6HR: 14/1400Z SFC/FL140 N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 FCST VA CLD +12HR: 14/2000Z SFC/FL140 N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 FCST VA CLD +18HR: 15/0200...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-14fa9d13488d80c8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has source elevation` | 12287 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12287 FT AMSL |
| `cand-1df40d4613ca3a3a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `expects volcanic ash movement` | toward the SSW through T+6 then SW by T+12 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA MVMT EXP TWD THE SSW THRU T+6 THEN SW BY T+12. |
| `cand-378a6af43ac52610` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has eruption activity detail` | light volcanic ash emissions observed | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: LGT VA EMS OBS |
| `cand-39f545114ff62ee7` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-3b37043169c020ee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has information sources` | GOES-19, webcam, NWP models | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. |
| `cand-3d202006efc4eab0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states forecast basis` | webcam observations and NWP models | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FL BASED ON WEBCAM OBS, FCST BASED ON NWP MDLS. |
| `cand-418481f58a34ea4d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was observed with vertical extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL140 N1446 W09133 - N1444 W09132 - N1437 W09139 - N1442 W09144 - N1446 W09133 |
| `cand-4c632a4755579ef9` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 30 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-4c93e5b569e52043` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was moving direction and speed` | southwest at 5 kt | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 5KT |
| `cand-57a09b96d466da3b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has volcano advisory bulletin` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-5bd9fd8b9ba3c6a3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast position at +6 hours` | SFC/FL140 near N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/1400Z SFC/FL140 N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 |
| `cand-6a952295598db94d` | `S2_llm_schema_slice` | `property_bundle` | `initiativeComments` | {"atm:initiativeComments": [{"evidence_text": "ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA", "value": "VOLCANIC ACTIVITY BULLETIN - SA... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-6c664a03092be6c5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `was observed at time` | 14/0800Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 14/0800Z |
| `cand-6d07a3388f3081d4` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 030", "value": 30}], "atm:initiativeComments": [{"evidence_text": "ATCSCC ADVZY 030 DCC 05/14/2026 VO... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-711f77717755412a` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-86f70d08fcf7e124` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is located in area` | Guatemala | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: SANTA MARIA 342030 PSN: N1445 W09133 AREA: GUATEMALA |
| `cand-a2bf3b5aa1aa0f78` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T08:34:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 08:36 |
| `cand-b8ef5117620430da` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory number` | 2026/237 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/237 |
| `cand-be1a51a5539de0d2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states possible light volcanic ash emissions observed on satellite and webcam` | moving southwest from summit | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PSBL LGT VA EMS OBS ON STLT AND WEBCAM MVG SW FM SUMMIT. |
| `cand-ccd1772ebcf760c1` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast position at +12 hours` | SFC/FL140 near N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/2000Z SFC/FL140 N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 |
| `cand-ea4cd23486a60bd4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective time window` | 140000-140000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140000-140000 |
| `cand-f552014b810af490` | `S1_llm_only` | `freeform_or_unmapped_fact` | `forecast position at +18 hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/0200Z NO VA EXP |

## ATCSCC-GOLD-052 / 2026-05-20:119

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=119
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09f2a56b834029e2` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | {"evidence_text": "CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z", "type": "nas:Airport"} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-1759c2b40772f203` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZBW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-38658a98ade8b318` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_controlled_entity'}` | {'class': 'airport', 'text': 'IAD'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-4838dda25cb1f997` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZID'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-5fa13fb3d2edb604` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZDC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-5fcb7197b24a2402` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_ground_stop'}` | {'class': 'traffic_management_action', 'text': 'CDM GROUND STOP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-6a032160ffe7526d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_new_maximum_delay_minutes'}` | {'class': 'delay_minutes_maximum', 'text': '73'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-6aac46489f046a31` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-702f83ad377ea86e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_impacting_condition'}` | {'class': 'weather_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-78f7a838e381a1a0` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD |
| `cand-7a7cb21f798b4df4` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-81f946976c6ab822` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_control_element'}` | {'class': 'airport', 'text': 'IAD'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, M... |
| `cand-857fa040e00674df` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_ground_stop_period'}` | {'class': 'time_window', 'text': '20/1900Z - 20/2015Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, M... |
| `cand-878c7af4e7d57082` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T19:12:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 19:12 |
| `cand-9554892111372a78` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T21:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201911-202115 |
| `cand-b0295f8e6fe385c0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-b0b3cec342f588dd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZTL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-b68ff1bbbe6f2a2c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZJX'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-b69c86602ec63f6b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states_probability_of_extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-b6f99de07ee25ba8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_new_total_delay_minutes'}` | {'class': 'delay_minutes_total', 'text': '1939'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-c19fc1a43b1fd1be` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies_facility_area'}` | {'class': 'facility_area', 'text': 'ZDC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-c804b66d3672c62a` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 119 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-c9d96ff12df7cb1f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZOB'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-e8d3a4ea511e6ff9` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP", "value": 119}], "atm:controlledNASelement": [{"evidence_text... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-e8e89e6e2c6b9638` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-f7a74de532d39557` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-fa8fadf43dc003ec` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports_new_average_delay_minutes'}` | {'class': 'delay_minutes_average', 'text': '48'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-fad05dd80044d277` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T19:11:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201911-202115 |

## ATCSCC-GOLD-053 / 2026-05-18:125

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=125
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 125 STL/ZKC 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2025Z GROUND STOP PERIOD: 18/1929Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0429f128c456f130` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element` | STL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL |
| `cand-12099287d9982e9d` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-1354aabf158553aa` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_maximum_delay` | 211 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-13858ddd9823ea9c` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T20:30:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:30 |
| `cand-221d82fd379e159c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `signature_time` | 26/05/18 20:30 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:30 |
| `cand-36d68ea181448c8a` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-3a7dd9ca22e279ce` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 182029-182230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182029-182230 |
| `cand-3d5cf236e640fafa` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-4681fcd07240e331` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 125 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 125 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-598f5f1f2bf46941` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-62d5199ee30c4c70` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_average_delay` | 116 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-69d4db374310ea01` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-7cedaf791bbfe809` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:29:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-7d0ca475d267395f` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2025Z GROUND STOP PERIOD: 18/1929Z - 18/2130Z", "value": "STL"}... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-8d82be281b171f4b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-8d8c44e56caee85f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_average_delay` | 175 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-9f77930304f4b64e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a19fbc0c69ef72d4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_previous_total_delays` | 927 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-a9cadccb7f072a70` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-af8c8bef525c1470` | `S1_llm_only` | `freeform_or_unmapped_fact` | `declares_ground_stop_period` | 18/1929Z - 18/2130Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-b97f3c122496b25c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-cb7c85dbdde22d8b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_maximum_delay` | 267 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-ce21fc0495b6a037` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_time_label` | 2025Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 2025Z |
| `cand-e5234b48537a52b9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facilities` | ZID | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZID |
| `cand-e7fbbede3d675271` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_total_delays` | 1403 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |

## ATCSCC-GOLD-054 / 2026-05-20:153

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=153
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 628 / 65 / 25 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1584 / 110 / 63 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: GROUN STOP EXTENDED. EFFECTIVE TIME: 202130-202315 SIGNATURE: 26/05/20 21:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-07f9c3db71115d7a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'declares ground stop period'}` | {'class': 'time_interval', 'text': '20/2114Z - 20/2215Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-09059648bcea9c5a` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-20T21:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 21:30 |
| `cand-09e1bc8e4722fe12` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-0d458bbc53561eea` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-20T21:14:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-1a87d71ed34edfd7` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2022b3128ec9cd3b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states advisory type'}` | {'class': 'ground_stop_advisory', 'text': 'CDM GROUND STOP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-208ee3f7a6365336` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-20T22:15:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-2c10c85351793284` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'states probability of extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-37e56b3b63d71819` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'lists impacting condition'}` | {'class': 'impacting_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-474a9edf3df56e50` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports previous total maximum average delays'}` | {'class': 'delay_statistics', 'text': '628 / 65 / 25'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 628 / 65 / 25 |
| `cand-52469d069237dd82` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-57b72cffed9a358a` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T21:30:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:30 |
| `cand-685e4dfa567b5161` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BWI | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BWI |
| `cand-6ca759ee111517d3` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T23:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202130-202315 |
| `cand-856015722c03e343` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8788226621e371a7` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'BWI', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-9790b784f134d242` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'notes comment about ground stop extension'}` | {'class': 'comment_statement', 'text': 'GROUN STOP EXTENDED.'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-a620e0b2cb1df43e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'gives effective time window'}` | {'class': 'effective_time_interval', 'text': '202130-202315'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202130-202315 |
| `cand-a7e24b41d33ee97c` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 153, "atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z -... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-ac3e070cfb425a68` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'identifies control element'}` | {'class': 'airport_control_element', 'text': 'BWI'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BWI |
| `cand-ae5375ae9b5719e1` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-be2cea68b0170f53` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 153 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-c8c9bd9a6e0a515a` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | GROUN STOP EXTENDED. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-d018f0928bcdd626` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | GROUN STOP EXTENDED. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-dca1ebcce5aa4c2b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes departure facilities'}` | {'class': 'facility_group', 'text': 'ZTL ZDC ZNY ZJX ZOB ZBW ZID'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-dec86b0483509ab6` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202130-202315 |
| `cand-e6b8c917c714c786` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'reports new total maximum average delays'}` | {'class': 'delay_statistics', 'text': '1584 / 110 / 63'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1584 / 110 / 63 |
| `cand-fbf0ab03e2b68b60` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |

## ATCSCC-GOLD-055 / 2026-05-20:179

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=179
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2300Z GROUND STOP PERIOD: 20/2249Z - 21/0000Z DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 921 / 281 / 77 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: LACK OF ROUTES EFFECTIVE TIME: 202300-210100 SIGNATURE: 26/05/20 23:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-002594d952e65896` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZOB'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-009cf140d19afb05` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-0837889ffcfe4bcd` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZDC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-08c8f86acf8b0668` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202300-210100 |
| `cand-0914a8c02ca60555` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element` | PHL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-1edf823c60aaff67` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T01:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202300-210100 |
| `cand-217e85b28129d61e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_comment` | LACK OF ROUTES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: LACK OF ROUTES |
| `cand-23c738897ca122eb` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZID'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-2d0cfac18d11ed70` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-3021afd6f6c0b254` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_new_total_maximum_average_delays` | 921 / 281 / 77 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 921 / 281 / 77 |
| `cand-31879aef60c10534` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_time` | 2300Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 2300Z |
| `cand-369550d29cd25aad` | `S1_llm_only` | `freeform_or_unmapped_fact` | `describes_flow_management_action` | GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-42ba7a4a01ca0280` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-4afd672532a607a4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-4e158a2bf41be0fe` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: PHL ELEMENT TYPE: APT", "value": "PHL"}], "atm:effectiveEndTime": [{"evidence_text": "GROUND ST... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-55331d4e66fafcc4` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `departureScope` | {'id': '_:depScope1', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-5a84223ed13a00ff` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-5d5b3681af37de1b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PHL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL |
| `cand-5e9c11cfcc6aef47` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | LACK OF ROUTES | `{"repaired_accepted": 1}` | `{}` | COMMENTS: LACK OF ROUTES |
| `cand-611482933b69703d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facilities` | ZDC ZOB ZID | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-677d91134641c8c5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_ground_stop_period` | 20/2249Z - 21/0000Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2249Z - 21/0000Z |
| `cand-6e2c29ed460292e5` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 179 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-6eecf8a9c22b4a39` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-7316d48d0801163f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_identifier` | ADVZY 179 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-77e2278025351915` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'type': 'nas:Airport', 'value': 'PHL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL ELEMENT TYPE: APT |
| `cand-92fe5f4b0252d7e8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 202300-210100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202300-210100 |
| `cand-d17f5917eca978aa` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 23:00 |
| `cand-f3c3b31c4552cbf6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `had_previous_total_maximum_average_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |

## ATCSCC-GOLD-056 / 2026-05-17:041

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=41
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 171639-172100 SIGNATURE: 26/05/17 16:39 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-19cdc0449dabc067` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has effective time` | 171639-172100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171639-172100 |
| `cand-32edac749b4b66d0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reason for implementing` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-3c515e2bd8890af2` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADVZY | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-4a391bc6bcb250a4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has advisory headline` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI |
| `cand-64ed73f7658c4356` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-7603f2e6a3bbe00e` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T16:39:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 16:39 |
| `cand-803e52d4253d7cd7` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-919c9766758aa4b8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is implementing` | CDRS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-b53ed0d986d5dc90` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 41, "atm:controlledNASelement": {"label": "MIA FLL CDRS_FYI", "type": "nas:Airport"}, "atm:effectiveEndTime": "2026-05-17T21:00:00", "... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-b9aa6d13329b92d0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states event time window` | 17/1300 - 17/2100 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 17/1300 - 17/2100 |
| `cand-bbf6f2f45812da76` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T16:39:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171639-172100 |
| `cand-c186abaaaa0bf8fd` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 41 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI |
| `cand-c343c41e9b05b0bd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `should fuel accordingly` | fuel accordingly | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-dd40ac896a89c3f6` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T21:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171639-172100 |
| `cand-e3294873a51aeaba` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies constrained facilities` | ZMA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-e68f7fa598f567b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `extends advisory` | ADVZY 024 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-ee449ec9d1037930` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 41 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |

## ATCSCC-GOLD-057 / 2026-05-14:007

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=7
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 35

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: FIRST TIER. EFFECTIVE TIME: 140030-140230 SIGNATURE: 26/05/14 00:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02fe74baaf3b3f8c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces ground stop for'}` | {'label': 'DCA', 'type': 'airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP |
| `cand-06ea133e20f7c765` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has new maximum delay'}` | {'label': '62', 'type': 'delay_minutes_maximum'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-07ca15379886638c` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-14T00:31:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/14 00:31 |
| `cand-0c4e445656eeb360` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 7 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 007 |
| `cand-1b2b8007478f8279` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140030-140230 |
| `cand-1ed15cc6c5a8344a` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | {"id": "dca", "name": "DCA", "type": "nas:Airport"} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-2f6bd9d6b5fa12a5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has ground stop period'}` | {'label': '13/2307Z - 14/0130Z', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 13/2307Z - 14/0130Z |
| `cand-3745c37110055769` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 7 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP |
| `cand-394c345ea552693c` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T00:31:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 00:31 |
| `cand-3cb31a6a8d34383b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesARTCC` | {'id': 'ZID', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-40a4ceea5c790b05` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-42dab946050590af` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesARTCC` | {'id': 'ZTL', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-449d14837524a5f7` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `withinARTCC` | {'id': '_:tier1', 'type': 'nas:ARTCCtier'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-45ba9ba83d6c18ed` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has controlling element'}` | {'label': 'DCA', 'type': 'airport_element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z |
| `cand-51ec07f4d6656a9d` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-56c470f7407e6d09` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesARTCC` | {'id': 'ZNY', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-66fbff86a75461d9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has new average delay'}` | {'label': '36', 'type': 'delay_minutes_average'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-71f19d3be7e11864` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-14T00:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140030-140230 |
| `cand-78e52663c304f9ea` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes departure facilities'}` | {'label': 'ZTL ZDC ZNY ZJX ZOB ZBW ZID', 'type': 'facility_list'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-79630d3f44f788a2` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesARTCC` | {'id': 'ZJX', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-7a76c6773f4c0038` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA |
| `cand-946db3f5a6d9541b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140030-140230 |
| `cand-9d6536d87dbac9de` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has probability of extension'}` | {'label': 'MEDIUM', 'type': 'extension_probability'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a46d47c4b328854f` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-ab4b4df09c1320b0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is impacted by'}` | {'label': 'WEATHER / THUNDERSTORMS', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-ab52c58bacf823d0` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-ad31163524c20fdf` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-14T02:30:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140030-140230 |
| `cand-af63e3ef94d27c0b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'id': 'DCA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-bb5870330ed4586b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesARTCC` | {'id': 'ZBW', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-d8238a9d9cd409c9` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `departureScope` | {'id': '_:as1', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-e850bd51a7528059` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesARTCC` | {'id': 'ZDC', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-ed8c3debefc560ee` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | FIRST TIER. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: FIRST TIER. |
| `cand-f07e1017cc1b6106` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-f8e56fa8b3d36baa` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesARTCC` | {'id': 'ZOB', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-f8ff71fc604d9fa7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has new total delay'}` | {'label': '580', 'type': 'delay_minutes_total'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |

## ATCSCC-GOLD-058 / 2026-05-20:139

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=139
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 2038Z GROUND STOP PERIOD: 20/2028Z - 20/2200Z CUMULATIVE PROGRAM PERIOD: 20/1930Z - 21/0359Z DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 571 / 129 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1722 / 148 / 78 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. EFFECTIVE TIME: 202042-202300 SIGNATURE: 26/05/20 20:43 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-20234283838dd2dc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_label` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-27f1f6f70af4acc3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-28e07529ef1ac360` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_ground_stop_period` | 20/2028Z - 20/2200Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2028Z - 20/2200Z |
| `cand-4167d7112208f17b` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CTL ELEMENT: DCA ELEMENT TYPE: APT", "value": "nas:Airport:DCA"}], "atm:effectiveEndTime": [{"evidence_text"... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-4b1269a8e91c5a6d` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-4db0cbe29c99dcf9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_new_total_max_average_delays` | {'average': 78, 'maximum': 148, 'total': 1722} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1722 / 148 / 78 |
| `cand-4e53b435ca7119d3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-5193d25d038aada8` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202042-202300 |
| `cand-5d5c4fff916cadfb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-646042a866811a39` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T20:43:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 20:43 |
| `cand-66d2172b1e167350` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_time` | 2038Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2038Z |
| `cand-6cf5885d850f1ff6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 202042-202300 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202042-202300 |
| `cand-6e743f3cb8b14751` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6fc8e28c1c0ed16f` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. |
| `cand-73d018dd6b583154` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-7bd37fbf4f74e2df` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_previous_total_max_average_delays` | {'average': 26, 'maximum': 129, 'total': 571} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 571 / 129 / 26 |
| `cand-837b9bb5cfbb9dea` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8e1130e12511f33c` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:42:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202042-202300 |
| `cand-99e619e951854a2c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departure_facilities` | ['ZTL', 'ZDC', 'ZNY', 'ZJX', 'ZOB', 'ZBW', 'ZID', 'CYHZ', 'CYOW', 'CYUL', 'CYYZ', 'CYTZ', 'CYQB'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-a3899af16474b699` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 139 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-ac60bb961e592bb6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_cumulative_program_period` | 20/1930Z - 21/0359Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 20/1930Z - 21/0359Z |
| `cand-c986155d2635c0d3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_signature_timestamp` | 26/05/20 20:43 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 20:43 |
| `cand-d88fc6d9086a2fb5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_comment` | LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. |
| `cand-e1adb58b994b1f66` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA |
| `cand-ec1c7e9c5a5938b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `imposes_action` | GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP |
| `cand-ecd0aae2f5e540b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `targets_control_element` | DCA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |

## ATCSCC-GOLD-059 / 2026-05-14:086

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=86
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 22

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 142157-150230 SIGNATURE: 26/05/14 21:57 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-011c8a168d17f0a6` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 86 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-07672f5b08e84127` | `S1_llm_only` | `freeform_or_unmapped_fact` | `says_users_can_expect` | airborne holding into the Minneapolis airport | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-079c64c159a8c4c7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `says_users_can_expect` | arrival delays | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-0d5dda71623d56e5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_title` | MSP AIRPORT ARRIVAL DELAYS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-1232dd607a5562d1` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 86, "atm:controlledNASelement": "nas:Airport", "atm:effectiveEndTime": "2026-05-15T02:30:00Z", "atm:effectiveStartTime": "2026-05-14T2... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-17f704b0aa1cdbda` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THE | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-1bf57bc3bdc02eea` | `S1_llm_only` | `freeform_or_unmapped_fact` | `gives_delay_cause` | thunderstorms | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-3f47b4877f15200d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `concerns_facility_group` | MSP/ZMP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-3f89d439a54dd4a6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `promises_follow_up_updates` | if necessary | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-65e73890bfe41c8c` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS", "value": 86}], "atm:effectiveEndTime": [{"evidenc... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-76a209f892c9e52d` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-891c6111be54ac7b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-8daf6f6ccbccede4` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-a82f9fe30eac85c9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `gives_delay_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-aed5dff9f64f1e7a` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 86, "atm:controlledNASelement": "nas:Airport", "atm:effectiveEndTime": "2026-05-15T02:30:00Z", "atm:effectiveStartTime": "2026-05-14T2... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-af30659b53b6d76e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_constrained_facility` | ZMP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMP |
| `cand-b538f124c8ca3a9a` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142157-150230 |
| `cand-b64e386fa83817f7` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 21:57 |
| `cand-c2091a2db9b95b78` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-c784eb6696202889` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_event_time_window` | 14/2200 - 15/0200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/2200 - 15/0200 |
| `cand-c932fc3fb0054e91` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_effective_time` | 142157-150230 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 142157-150230 |
| `cand-e53580f163a7233c` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142157-150230 |

## ATCSCC-GOLD-060 / 2026-05-17:050

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=50
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 16

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 1814Z GS CNX PERIOD: 17/1814Z - 17/2020Z COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z EFFECTIVE TIME: 171815-172120 SIGNATURE: 26/05/17 18:17 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-07cb30e36f6c3216` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T21:20:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171815-172120 |
| `cand-139e392cb5f1f952` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_effective_time_window` | 171815-172120 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171815-172120 |
| `cand-21fa77b3d9302310` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T18:17:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 18:17 |
| `cand-32ab0a0c7f267ab4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `warns_of_increased_scheduling_delays` | aircraft within 1st tiers until 2000Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-40202b3bc92c6649` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_advisory_time` | 1814Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1814Z |
| `cand-5a1a2631e590e5cf` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T18:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171815-172120 |
| `cand-5de20d284fcda321` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'label': 'DCA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 1814Z GS CNX PERIOD: 17/1814Z - 17/2020Z COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-64217ab06008603f` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA |
| `cand-8059fdfca00f7fd4` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-85160164bc2c9ca9` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 50 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX |
| `cand-aeaecc7481240898` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-d0b74b1b31e6ae4a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_header` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX |
| `cand-e1c619791dc1bba4` | `S1_llm_only` | `freeform_or_unmapped_fact` | `names_control_element` | DCA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-e32e512794afe1a5` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"evidence_text": "CTL ELEMENT: DCA ELEMENT TYPE: APT", "value": "nas:Airport"}, "atm:effectiveEndTime": {"evidence_text": "GS C... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-f0ff1268c4bd866a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `defines_effective_period` | 17/1814Z - 17/2020Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 17/1814Z - 17/2020Z |
| `cand-f920f97aff7da13e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `reports_ground_stop_cancellation` | GS CNX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
