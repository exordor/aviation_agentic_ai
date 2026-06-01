# NASA ATMONTO Gold Review batch_06

- Samples: `ATCSCC-GOLD-051` to `ATCSCC-GOLD-060`
- Records: 10
- Candidate clusters: 299

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
- Candidate clusters: 24

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA MESSAGE: FVXX21 KNES 140834 WSI DDS:140836 VA ADVISORY DTG: 20260514/0834Z VAAC: WASHINGTON VOLCANO: SANTA MARIA 342030 PSN: N1445 W09133 AREA: GUATEMALA SOURCE ELEV: 12287 FT AMSL ADVISORY NR: 2026/237 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: LGT VA EMS OBS VA DTG: 14/0800Z OBS VA CLD: SFC/FL140 N1446 W09133 - N1444 W09132 - N1437 W09139 - N1442 W09144 - N1446 W09133 MOV SW 5KT FCST VA CLD +6HR: 14/1400Z SFC/FL140 N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 FCST VA CLD +12HR: 14/2000Z SFC/FL140 N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 FCST VA CLD +18HR: 15/0200...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1f0306c10cc34a92` | `S1_llm_only` | `canonical_fact` | `expects volcanic ash movement` | toward the SSW through T+6 then SW by T+12 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA MVMT EXP TWD THE SSW THRU T+6 THEN SW BY T+12. |
| `cand-22c7eed68e849857` | `S1_llm_only` | `canonical_fact` | `has source elevation` | 12287 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12287 FT AMSL |
| `cand-2604004e9b51dd91` | `S1_llm_only` | `canonical_fact` | `states possible light volcanic ash emissions observed on satellite and webcam` | moving southwest from summit | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PSBL LGT VA EMS OBS ON STLT AND WEBCAM MVG SW FM SUMMIT. |
| `cand-276a67fda13a7ec1` | `S1_llm_only` | `canonical_fact` | `states forecast basis` | webcam observations and NWP models | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FL BASED ON WEBCAM OBS, FCST BASED ON NWP MDLS. |
| `cand-34468c26c6098cab` | `S1_llm_only` | `canonical_fact` | `was moving direction and speed` | southwest at 5 kt | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 5KT |
| `cand-39bb12da635e0bfd` | `S1_llm_only` | `canonical_fact` | `was observed with vertical extent` | SFC/FL140 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL140 N1446 W09133 - N1444 W09132 - N1437 W09139 - N1442 W09144 - N1446 W09133 |
| `cand-39f545114ff62ee7` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-4c632a4755579ef9` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 30 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-51e505d0806f6f95` | `S1_llm_only` | `canonical_fact` | `has information sources` | GOES-19, webcam, NWP models | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. |
| `cand-63cfdfc02d14adde` | `S1_llm_only` | `canonical_fact` | `was observed at time` | 14/0800Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 14/0800Z |
| `cand-711f77717755412a` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-90219569d8587832` | `S1_llm_only` | `canonical_fact` | `forecast position at +12 hours` | SFC/FL140 near N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/2000Z SFC/FL140 N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 |
| `cand-a01c426c457037c9` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 30 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 030 |
| `cand-a0529978e2816567` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - SANTA MARIA | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-a2bf3b5aa1aa0f78` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T08:34:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 08:36 |
| `cand-a411a33bf361a288` | `S1_llm_only` | `canonical_fact` | `effective time window` | 140000-140000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140000-140000 |
| `cand-aee0f523944db02f` | `S1_llm_only` | `canonical_fact` | `has eruption activity detail` | light volcanic ash emissions observed | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: LGT VA EMS OBS |
| `cand-b7db93ba1efe6090` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T08:36:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 08:36 |
| `cand-b8233ae37e8647a7` | `S1_llm_only` | `canonical_fact` | `is located in area` | Guatemala | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: SANTA MARIA 342030 PSN: N1445 W09133 AREA: GUATEMALA |
| `cand-d7e6b778c5c05e8b` | `S1_llm_only` | `canonical_fact` | `forecast position at +18 hours` | no volcanic ash expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/0200Z NO VA EXP |
| `cand-e29fdee288ac3baf` | `S1_llm_only` | `canonical_fact` | `has advisory number` | 2026/237 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/237 |
| `cand-e57efb8af8879b6e` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - SANTA | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-f03f2b5a04f1bbb6` | `S1_llm_only` | `canonical_fact` | `forecast position at +6 hours` | SFC/FL140 near N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/1400Z SFC/FL140 N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 |
| `cand-fdfa6d00e2ef62c6` | `S1_llm_only` | `canonical_fact` | `has volcano advisory bulletin` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |

## ATCSCC-GOLD-052 / 2026-05-20:119

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=119
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 34

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03b5b7f1ad989dc8` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-1c3d7d678f65b530` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZTL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-1da7a2b517a92b02` | `S1_llm_only` | `canonical_fact` | `'has_impacting_condition'}` | {'class': 'weather_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-2161dafd31b53a65` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZOB'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-25342a04d7d03dea` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZBW'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-2c0a1426cea1945e` | `S1_llm_only` | `canonical_fact` | `'has_control_element'}` | {'class': 'airport', 'text': 'IAD'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, M... |
| `cand-3549fb9b0978f4fd` | `S1_llm_only` | `canonical_fact` | `'identifies_facility_area'}` | {'class': 'facility_area', 'text': 'ZDC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-5273f5dab86b7c6c` | `S1_llm_only` | `canonical_fact` | `'reports_new_average_delay_minutes'}` | {'class': 'delay_minutes_average', 'text': '48'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-532a0b4229d58b99` | `S1_llm_only` | `canonical_fact` | `'has_ground_stop_period'}` | {'class': 'time_window', 'text': '20/1900Z - 20/2015Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, M... |
| `cand-62591f2fdf6257e9` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-6aac46489f046a31` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-78f7a838e381a1a0` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAD | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD |
| `cand-79c9b6e13662e986` | `S1_llm_only` | `canonical_fact` | `'states_probability_of_extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-7a7cb21f798b4df4` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-878c7af4e7d57082` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T19:12:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/20 19:12 |
| `cand-9554892111372a78` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T21:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201911-202115 |
| `cand-a1934673633dc56f` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZJX'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-a7d9c96bebdf59fe` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZDC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-b8ec95a2eae0238d` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZID'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-b9f8a5d6dfc97aba` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T20:15:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-bc86be0369f68cdf` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | {"evidence_text": "CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z", "type": "nas:Airport"} | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z |
| `cand-c221711026fdba3c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T20:15:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/1900Z - 20/2015Z |
| `cand-c2748b7b9c752373` | `S1_llm_only` | `canonical_fact` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-c804b66d3672c62a` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 119 | `{"repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-cdcbf196db45c224` | `S1_llm_only` | `canonical_fact` | `'announces_ground_stop'}` | {'class': 'traffic_management_action', 'text': 'CDM GROUND STOP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-ce3ad729b93e52a3` | `S1_llm_only` | `canonical_fact` | `'reports_new_total_delay_minutes'}` | {'class': 'delay_minutes_total', 'text': '1939'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-cef6c0e8a8d22bfa` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T19:00:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/1900Z - 20/2015Z |
| `cand-d26d0395dd1eb103` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD ELEMENT TYPE: APT |
| `cand-de018e8cba746389` | `S1_llm_only` | `canonical_fact` | `'reports_new_maximum_delay_minutes'}` | {'class': 'delay_minutes_maximum', 'text': '73'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-e167598435cdfdb3` | `S1_llm_only` | `canonical_fact` | `'identifies_controlled_entity'}` | {'class': 'airport', 'text': 'IAD'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-e4fe9dbf3819f4bb` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T19:00:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-e8e89e6e2c6b9638` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-f7a74de532d39557` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-fad05dd80044d277` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T19:11:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201911-202115 |

## ATCSCC-GOLD-053 / 2026-05-18:125

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=125
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 125 STL/ZKC 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2025Z GROUND STOP PERIOD: 18/1929Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0cac4baf1773ea3a` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | STL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2025Z GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-12099287d9982e9d` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-13858ddd9823ea9c` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T20:30:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/18 20:30 |
| `cand-36d68ea181448c8a` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| M... | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Vi... |
| `cand-3d5cf236e640fafa` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-3f9d8ad2f6135324` | `S1_llm_only` | `canonical_fact` | `signature_time` | 26/05/18 20:30 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:30 |
| `cand-4681fcd07240e331` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 125 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 125 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-47ded313bc0738c2` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 182029-182230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182029-182230 |
| `cand-4d49f6aa2522b0c7` | `S1_llm_only` | `canonical_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-507d58fab93a01a4` | `S1_llm_only` | `canonical_fact` | `declares_ground_stop_period` | 18/1929Z - 18/2130Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-598f5f1f2bf46941` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-5aa66f87b45ab81f` | `S1_llm_only` | `canonical_fact` | `includes_departure_facilities` | ZID | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZID |
| `cand-5bcab9f476aacc6e` | `S1_llm_only` | `canonical_fact` | `has_time_label` | 2025Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 2025Z |
| `cand-75dca5e5aa1660e5` | `S1_llm_only` | `canonical_fact` | `has_control_element` | STL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL |
| `cand-7cedaf791bbfe809` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:29:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-81276727aac4f908` | `S1_llm_only` | `canonical_fact` | `has_new_maximum_delay` | 267 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-820a7ec44a436d6e` | `S1_llm_only` | `canonical_fact` | `has_previous_total_delays` | 927 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-86cdb0dabd9ff12f` | `S1_llm_only` | `canonical_fact` | `has_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-89500a8108cb55f3` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EFFECTIVE TIME: 182029-182230 | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-8d82be281b171f4b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-91395b74551e1b73` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T21:30:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-9afb3e39353440a0` | `S1_llm_only` | `canonical_fact` | `has_new_average_delay` | 175 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-a9cadccb7f072a70` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-ba24b7ba081a99dd` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T19:29:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-dbd1d250aae72e01` | `S1_llm_only` | `canonical_fact` | `has_new_total_delays` | 1403 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-e8bb8937efa64e10` | `S1_llm_only` | `canonical_fact` | `has_previous_maximum_delay` | 211 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-ee0be780043e9faa` | `S1_llm_only` | `canonical_fact` | `has_previous_average_delay` | 116 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-eec142cf318a3025` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-054 / 2026-05-20:153

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=153
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 35

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 628 / 65 / 25 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1584 / 110 / 63 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: GROUN STOP EXTENDED. EFFECTIVE TIME: 202130-202315 SIGNATURE: 26/05/20 21:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09e1bc8e4722fe12` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-0f2d122ab727c7a1` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-14062b552798e281` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | GROUN STOP EXTENDED. | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-18ac61f190056366` | `S1_llm_only` | `canonical_fact` | `'reports previous total maximum average delays'}` | {'class': 'delay_statistics', 'text': '628 / 65 / 25'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 628 / 65 / 25 |
| `cand-1a45287aa0a9318a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2f54036d68ec37ae` | `S1_llm_only` | `canonical_fact` | `'states probability of extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-3275ddb90364c26b` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-337a2d76c001565b` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | BWI | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-41d11745669b90df` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:14:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-52469d069237dd82` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-52669e100b827362` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T21:24:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-57b72cffed9a358a` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T21:30:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:30 |
| `cand-5c0d996953035406` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-63bc22bfda199f46` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T22:15:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-685e4dfa567b5161` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BWI | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BWI |
| `cand-6ca759ee111517d3` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T23:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202130-202315 |
| `cand-6d41286bcf36f186` | `S1_llm_only` | `canonical_fact` | `'notes comment about ground stop extension'}` | {'class': 'comment_statement', 'text': 'GROUN STOP EXTENDED.'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-7a2add7a6f4eb443` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T22:15:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-856015722c03e343` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8f5ee492b39ece79` | `S1_llm_only` | `canonical_fact` | `'states advisory type'}` | {'class': 'ground_stop_advisory', 'text': 'CDM GROUND STOP'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-a45d243ecf475214` | `S1_llm_only` | `canonical_fact` | `'declares ground stop period'}` | {'class': 'time_interval', 'text': '20/2114Z - 20/2215Z'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-aaf422efb6dda6d0` | `S1_llm_only` | `canonical_fact` | `'gives effective time window'}` | {'class': 'effective_time_interval', 'text': '202130-202315'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202130-202315 |
| `cand-ac660c2f029ddeae` | `S1_llm_only` | `canonical_fact` | `'reports new total maximum average delays'}` | {'class': 'delay_statistics', 'text': '1584 / 110 / 63'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1584 / 110 / 63 |
| `cand-b41e7b984bed4b5a` | `S1_llm_only` | `canonical_fact` | `'includes departure facilities'}` | {'class': 'facility_group', 'text': 'ZTL ZDC ZNY ZJX ZOB ZBW ZID'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-be2cea68b0170f53` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 153 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-c7f85d52bf2a1422` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 153 | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-cc7872e5ad5b3b3b` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:14:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-cd2e9aef6a226797` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | {'label': 'BWI', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-d018f0928bcdd626` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | GROUN STOP EXTENDED. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-d2d865108d1eb96b` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | GROUN STOP EXTENDED. | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-dec86b0483509ab6` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202130-202315 |
| `cand-df55753fa2614c16` | `S1_llm_only` | `canonical_fact` | `'lists impacting condition'}` | {'class': 'impacting_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e17190612808c41f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `type` | atm:GroundStopTMI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-ec3318af48c1ae8d` | `S1_llm_only` | `canonical_fact` | `'identifies control element'}` | {'class': 'airport_control_element', 'text': 'BWI'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BWI |
| `cand-f6008ad9b48d3967` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-20T21:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 21:30 |

## ATCSCC-GOLD-055 / 2026-05-20:179

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=179
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 30

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2300Z GROUND STOP PERIOD: 20/2249Z - 21/0000Z DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 921 / 281 / 77 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: LACK OF ROUTES EFFECTIVE TIME: 202300-210100 SIGNATURE: 26/05/20 23:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-009cf140d19afb05` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-08c8f86acf8b0668` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202300-210100 |
| `cand-199ebb84311b4779` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | PHL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT |
| `cand-1d9b3989e009a661` | `S1_llm_only` | `canonical_fact` | `has_comment` | LACK OF ROUTES | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: LACK OF ROUTES |
| `cand-1ec51c6164ddb5c3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZOB'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-1edf823c60aaff67` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T01:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202300-210100 |
| `cand-2d0cfac18d11ed70` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2efe9251b2500267` | `S1_llm_only` | `canonical_fact` | `has_advisory_time` | 2300Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 2300Z |
| `cand-39e478306be1fa0f` | `S1_llm_only` | `canonical_fact` | `has_ground_stop_period` | 20/2249Z - 21/0000Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2249Z - 21/0000Z |
| `cand-42088cca6d66062e` | `S1_llm_only` | `canonical_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-46eca9c909123bb2` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 202300-210100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202300-210100 |
| `cand-4745e7af87eb0764` | `S1_llm_only` | `canonical_fact` | `has_advisory_identifier` | ADVZY 179 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-57bb51476af6a1d5` | `S1_llm_only` | `canonical_fact` | `had_previous_total_maximum_average_delays` | 0 / 0 / 0 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-5d5b3681af37de1b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PHL | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL |
| `cand-5e9c11cfcc6aef47` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | LACK OF ROUTES | `{"repaired_accepted": 2}` | `{}` | COMMENTS: LACK OF ROUTES |
| `cand-6e2c29ed460292e5` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 179 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-6eecf8a9c22b4a39` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-7c4a0fe85ed605d6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | {'type': 'nas:Airport', 'value': 'PHL'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL ELEMENT TYPE: APT |
| `cand-8af791243df59ffe` | `S1_llm_only` | `canonical_fact` | `describes_flow_management_action` | GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-9769c11f8231dbc3` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `departureScope` | {'id': '_:depScope1', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-99dc74a2f9869180` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZID'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-9eb1adeb15113ffd` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2249Z - 21/0000Z |
| `cand-a1cd18f4b996a0d8` | `S1_llm_only` | `canonical_fact` | `has_control_element` | PHL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-aa127eafa7a7d823` | `S1_llm_only` | `canonical_fact` | `includes_departure_facilities` | ZDC ZOB ZID | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-d17f5917eca978aa` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T23:00:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/20 23:00 |
| `cand-dadd8bf98defe2b5` | `S1_llm_only` | `canonical_fact` | `has_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-e1fb2672284ec6a2` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T22:49:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2249Z - 21/0000Z |
| `cand-e39343247381d0e8` | `S1_llm_only` | `canonical_fact` | `has_new_total_maximum_average_delays` | 921 / 281 / 77 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 921 / 281 / 77 |
| `cand-ef2ba2a4a60a39dc` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZDC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-fd160b9594124ef9` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-056 / 2026-05-17:041

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=41
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 171639-172100 SIGNATURE: 26/05/17 16:39 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0130c0f2af55b34f` | `S1_llm_only` | `canonical_fact` | `should fuel accordingly` | fuel accordingly | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-047cdf1363aa9181` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-0ce691ecb215afaa` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T21:00:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-212ece368b5e51a6` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 41 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-270cb0858ed53be0` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T16:39:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-2d6d8e2b985e3b4b` | `S1_llm_only` | `canonical_fact` | `has effective time` | 171639-172100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171639-172100 |
| `cand-3c515e2bd8890af2` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADVZY | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-48e6e63ebdaf3e0f` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | MIA FLL CDRS_FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-5762bbdc0be294fc` | `S1_llm_only` | `canonical_fact` | `has advisory headline` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI |
| `cand-6216845ee81ca766` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | CDR | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-63b53a68002887e4` | `S1_llm_only` | `canonical_fact` | `identifies constrained facilities` | ZMA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-64ed73f7658c4356` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-6d960982e3178b43` | `S1_llm_only` | `canonical_fact` | `extends advisory` | ADVZY 024 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-70fc21f4b8ee5223` | `S1_llm_only` | `canonical_fact` | `reason for implementing` | weather | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-729a4480f087ead5` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-72f44f3d79a77dcf` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-17T16:39:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-7603f2e6a3bbe00e` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T16:39:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 16:39 |
| `cand-7a80c6758561a6fa` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-17T16:39:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-803e52d4253d7cd7` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-999e8d7b8bd05b35` | `S1_llm_only` | `canonical_fact` | `is implementing` | CDRS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-bbf6f2f45812da76` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T16:39:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171639-172100 |
| `cand-c186abaaaa0bf8fd` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 41 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI |
| `cand-c3dad3e14736ecea` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 41 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-d73c3e55d6c185e2` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | USERS SHOULD FUEL ACCORDINGLY. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-dd40ac896a89c3f6` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T21:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171639-172100 |
| `cand-ef3e7fbff55b862c` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE T... |
| `cand-f3724fe995697939` | `S1_llm_only` | `canonical_fact` | `states event time window` | 17/1300 - 17/2100 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 17/1300 - 17/2100 |

## ATCSCC-GOLD-057 / 2026-05-14:007

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=7
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 37

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: FIRST TIER. EFFECTIVE TIME: 140030-140230 SIGNATURE: 26/05/14 00:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00ff70d7ec28296f` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T02:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140030-140230 |
| `cand-0779a10be34f8587` | `S1_llm_only` | `canonical_fact` | `'has new maximum delay'}` | {'label': '62', 'type': 'delay_minutes_maximum'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-0beef83410f72a58` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | dca | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-0cc999668a1216d1` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:30:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140030-140230 |
| `cand-1b2b8007478f8279` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-14T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140030-140230 |
| `cand-1c14c9fbe3d94723` | `S2_llm_schema_slice` | `canonical_fact` | `includesARTCC` | {'id': 'ZOB', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-201c7ed2bbca9dc9` | `S1_llm_only` | `canonical_fact` | `'is impacted by'}` | {'label': 'WEATHER / THUNDERSTORMS', 'type': 'impacting_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-261625e482afb014` | `S1_llm_only` | `canonical_fact` | `'has new total delay'}` | {'label': '580', 'type': 'delay_minutes_total'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-312604950974ded1` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {'id': 'DCA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-3745c37110055769` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 7 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP |
| `cand-3754c9163126d92a` | `S2_llm_schema_slice` | `canonical_fact` | `includesARTCC` | {'id': 'ZTL', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-394c345ea552693c` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T00:31:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 00:31 |
| `cand-3eac9bd85813aaab` | `S1_llm_only` | `canonical_fact` | `'has ground stop period'}` | {'label': '13/2307Z - 14/0130Z', 'type': 'time_interval'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 13/2307Z - 14/0130Z |
| `cand-40a4ceea5c790b05` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-4dc332b0d61eb4aa` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-51ec07f4d6656a9d` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-530a420095cd4378` | `S1_llm_only` | `canonical_fact` | `'announces ground stop for'}` | {'label': 'DCA', 'type': 'airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP |
| `cand-5770231af98ae5d2` | `S1_llm_only` | `canonical_fact` | `'includes departure facilities'}` | {'label': 'ZTL ZDC ZNY ZJX ZOB ZBW ZID', 'type': 'facility_list'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-67fe35473cd9f772` | `S2_llm_schema_slice` | `canonical_fact` | `includesARTCC` | {'id': 'ZNY', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-7a76c6773f4c0038` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA |
| `cand-83ec5b21411aa36e` | `S2_llm_schema_slice` | `canonical_fact` | `includesARTCC` | {'id': 'ZJX', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-946db3f5a6d9541b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T00:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140030-140230 |
| `cand-9984cc71ae9ca7af` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PR... |
| `cand-a13dfffc2c8c78dc` | `S1_llm_only` | `canonical_fact` | `'has probability of extension'}` | {'label': 'MEDIUM', 'type': 'extension_probability'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a46d47c4b328854f` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a9003c7e001c8ce6` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-b6a7159e2fb74f0a` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T00:31:00Z | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/14 00:31 |
| `cand-bbe80583d729bcf6` | `S2_llm_schema_slice` | `canonical_fact` | `departureScope` | {'id': '_:as1', 'type': 'atm:AirportSpec'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-bf18fc09b1e4a925` | `S2_llm_schema_slice` | `canonical_fact` | `includesARTCC` | {'id': 'ZBW', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-c6957789d6a16e69` | `S1_llm_only` | `canonical_fact` | `'has new average delay'}` | {'label': '36', 'type': 'delay_minutes_average'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-cc3e3eca3fa5bda4` | `S1_llm_only` | `canonical_fact` | `'has controlling element'}` | {'label': 'DCA', 'type': 'airport_element'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z |
| `cand-d5985bc576cac33f` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 7 | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 007 |
| `cand-db01832d8feea916` | `S2_llm_schema_slice` | `canonical_fact` | `includesARTCC` | {'id': 'ZDC', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-e7042b6bc82137ad` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-ed8c3debefc560ee` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | FIRST TIER. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: FIRST TIER. |
| `cand-f55f5274abb97aa8` | `S2_llm_schema_slice` | `canonical_fact` | `includesARTCC` | {'id': 'ZID', 'type': 'nas:ARTCC'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-f68f674f945c0713` | `S2_llm_schema_slice` | `canonical_fact` | `withinARTCC` | {'id': '_:tier1', 'type': 'nas:ARTCCtier'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |

## ATCSCC-GOLD-058 / 2026-05-20:139

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=139
- Candidate class: `GroundStopTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 28

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 2038Z GROUND STOP PERIOD: 20/2028Z - 20/2200Z CUMULATIVE PROGRAM PERIOD: 20/1930Z - 21/0359Z DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 571 / 129 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1722 / 148 / 78 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. EFFECTIVE TIME: 202042-202300 SIGNATURE: 26/05/20 20:43 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02bf0130c18d13eb` | `S1_llm_only` | `canonical_fact` | `has_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-030021db1861f5a9` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-1e72958b2e6ea237` | `S1_llm_only` | `canonical_fact` | `has_advisory_label` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-1e96c871d6ac6686` | `S1_llm_only` | `canonical_fact` | `imposes_action` | GROUND STOP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP |
| `cand-36d29eab0f505885` | `S1_llm_only` | `canonical_fact` | `has_signature_timestamp` | 26/05/20 20:43 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 20:43 |
| `cand-3d41e07a1188e07c` | `S1_llm_only` | `canonical_fact` | `has_ground_stop_period` | 20/2028Z - 20/2200Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2028Z - 20/2200Z |
| `cand-40eac1be7575b29f` | `S1_llm_only` | `canonical_fact` | `has_advisory_time` | 2038Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2038Z |
| `cand-4b1269a8e91c5a6d` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-5193d25d038aada8` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202042-202300 |
| `cand-546d1da359cb7c27` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:28:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2028Z - 20/2200Z |
| `cand-6066104069ad1b82` | `S1_llm_only` | `canonical_fact` | `states_comment` | LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. |
| `cand-610ed2a7437ae960` | `S1_llm_only` | `canonical_fact` | `reports_previous_total_max_average_delays` | {'average': 26, 'maximum': 129, 'total': 571} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 571 / 129 / 26 |
| `cand-646042a866811a39` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T20:43:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/20 20:43 |
| `cand-6e743f3cb8b14751` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6fc8e28c1c0ed16f` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. | `{"repaired_accepted": 2}` | `{}` | COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. |
| `cand-837b9bb5cfbb9dea` | `S0_rule_only, S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-868af18addebc2e5` | `S1_llm_only` | `canonical_fact` | `has_cumulative_program_period` | 20/1930Z - 21/0359Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 20/1930Z - 21/0359Z |
| `cand-8b9a008c6fba7d60` | `S1_llm_only` | `canonical_fact` | `includes_departure_facilities` | ['ZTL', 'ZDC', 'ZNY', 'ZJX', 'ZOB', 'ZBW', 'ZID', 'CYHZ', 'CYOW', 'CYUL', 'CYYZ', 'CYTZ', 'CYQB'] | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-8e1130e12511f33c` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:42:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202042-202300 |
| `cand-9f69a54fc3cd2b4d` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport:DCA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA ELEMENT TYPE: APT |
| `cand-a3899af16474b699` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 139 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-a64d3e442f381128` | `S1_llm_only` | `canonical_fact` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-bdf494645b5c1019` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 202042-202300 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202042-202300 |
| `cand-e1adb58b994b1f66` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA |
| `cand-e38414225995c1d1` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T22:00:00Z | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2028Z - 20/2200Z |
| `cand-e8b9a3491d2ef251` | `S1_llm_only` | `canonical_fact` | `reports_new_total_max_average_delays` | {'average': 78, 'maximum': 148, 'total': 1722} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1722 / 148 / 78 |
| `cand-ea0e1bed2d7eef53` | `S1_llm_only` | `canonical_fact` | `targets_control_element` | DCA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-ee006350b973bbfc` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-059 / 2026-05-14:086

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=86
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 34

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 142157-150230 SIGNATURE: 26/05/14 21:57 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-011c8a168d17f0a6` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 86 | `{"repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-044ec392d6c4e4a3` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-068d97afee5ef5a9` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. | `{"repaired_accepted": 1}` | `{}` | ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-0d7053deeec50e64` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-1102bd9b1fd2dea5` | `S1_llm_only` | `canonical_fact` | `identifies_constrained_facility` | ZMP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMP |
| `cand-16810545d5bd5746` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-17f704b0aa1cdbda` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THE | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-19c576a61f2066c5` | `S1_llm_only` | `canonical_fact` | `has_advisory_title` | MSP AIRPORT ARRIVAL DELAYS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-42b3b6f82a405cdd` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | MSP AIRPORT ARRIVAL DELAYS | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-4618c852fcf78b7f` | `S1_llm_only` | `canonical_fact` | `states_event_time_window` | 14/2200 - 15/0200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/2200 - 15/0200 |
| `cand-5b02bc7158ad4af0` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-14T21:57:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 21:57 |
| `cand-65b8b507ef633b2c` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-660e4d7494b665a4` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-6f894e047871ea17` | `S1_llm_only` | `canonical_fact` | `concerns_facility_group` | MSP/ZMP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-76a209f892c9e52d` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-82c657b167983f84` | `S1_llm_only` | `canonical_fact` | `says_users_can_expect` | arrival delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-891c6111be54ac7b` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-8daf6f6ccbccede4` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-9ebf908fd6516b39` | `S1_llm_only` | `canonical_fact` | `gives_delay_cause` | thunderstorms | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-a215b06645b62fce` | `S1_llm_only` | `canonical_fact` | `says_users_can_expect` | airborne holding into the Minneapolis airport | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-b38bfb7831639137` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-b538f124c8ca3a9a` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T02:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142157-150230 |
| `cand-b64e386fa83817f7` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 21:57 |
| `cand-ba36a24473c0a65b` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-bbb6ccd1012a5bcc` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T22:00:00 | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 |
| `cand-bc80e0c4447959d8` | `S1_llm_only` | `canonical_fact` | `promises_follow_up_updates` | if necessary | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-bcd80a5d897c39b3` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-beb0fb2aa07ca50f` | `S1_llm_only` | `canonical_fact` | `gives_delay_duration` | up to 30 minutes | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-c2091a2db9b95b78` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-c352f1ea8b5585e9` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T02:00:00 | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 |
| `cand-d96b06b77ee8cc61` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 86 | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-e125c3d602fab938` | `S1_llm_only` | `canonical_fact` | `states_effective_time` | 142157-150230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 142157-150230 |
| `cand-e53580f163a7233c` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-14T21:57:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142157-150230 |
| `cand-fba80025a85444d8` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |

## ATCSCC-GOLD-060 / 2026-05-17:050

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=50
- Candidate class: `TrafficManagementInitiative`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 22

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
| `cand-21fa77b3d9302310` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-17T18:17:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 18:17 |
| `cand-2396102cda51b834` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T20:20:00Z | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 17/1814Z - 17/2020Z |
| `cand-3498ee0b686aee57` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-17T18:14:00Z | `{"repaired_accepted": 1}` | `{}` | ADL TIME: 1814Z |
| `cand-4329e715a9087238` | `S1_llm_only` | `canonical_fact` | `names_control_element` | DCA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-45835fd4e0719059` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA ELEMENT TYPE: APT |
| `cand-5585191f084faa37` | `S1_llm_only` | `canonical_fact` | `has_advisory_header` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX |
| `cand-55afa3a8e586b33e` | `S1_llm_only` | `canonical_fact` | `states_effective_time_window` | 171815-172120 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171815-172120 |
| `cand-5a1a2631e590e5cf` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T18:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171815-172120 |
| `cand-64217ab06008603f` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA |
| `cand-67e6099c84f011a8` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `controlledNASelement` | {'label': 'DCA', 'type': 'nas:Airport'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 1814Z GS CNX PERIOD: 17/1814Z - 17/2020Z COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-687642ff13595085` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T18:14:00Z | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 17/1814Z - 17/2020Z |
| `cand-6fae7db178709c59` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-8059fdfca00f7fd4` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-85160164bc2c9ca9` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 50 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX |
| `cand-86b62eb0dc305f2b` | `S1_llm_only` | `canonical_fact` | `reports_ground_stop_cancellation` | GS CNX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-8e077e929993666e` | `S1_llm_only` | `canonical_fact` | `defines_effective_period` | 17/1814Z - 17/2020Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 17/1814Z - 17/2020Z |
| `cand-929b6d7ed54001ea` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-9bd1d506b2ce5350` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | NONE | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 17/1814Z - 17/2020Z |
| `cand-a0b3f974528ba2d1` | `S1_llm_only` | `canonical_fact` | `warns_of_increased_scheduling_delays` | aircraft within 1st tiers until 2000Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-efbf193a7d307464` | `S1_llm_only` | `canonical_fact` | `states_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-fd432e92fa75a58a` | `S1_llm_only` | `canonical_fact` | `states_advisory_time` | 1814Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1814Z |
