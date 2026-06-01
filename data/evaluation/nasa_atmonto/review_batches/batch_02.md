# NASA ATMONTO Gold Review batch_02

- Samples: `ATCSCC-GOLD-011` to `ATCSCC-GOLD-020`
- Records: 10
- Candidate clusters: 286

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-011 / 2026-05-19:108

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=108
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL MESSAGE: NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 192115 TO 200000 PROBABILITY OF EXTENSION: MODERATE REMARKS: FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST HIGHER ALTITUDE. JETS=10000 ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KBOS KJFK >BURDY T358 SEY ARCAV ORCHA CCC V46 DPK JFK < KBOS KHPN >BOSOX T303 MAD EEGOR < EEGOR1 KBOS KLGA >BOSOX T303 MAD EEGOR PRENO < KBOS KDXR >BOSOX T303 MAD EEGOR < EEGOR1 KBOS KEWR KTEB KMMU >BOSOX T303 HFD...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-051f509562064271` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL", "value": 108}], "atm:controlledNASelement": [{"evidence_text": "CO... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-0aedf634bbeba826` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective_time` | 192115-200000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192115-200000 |
| `cand-142b21005ca21926` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_valid_from_to` | ETD 192115 to 200000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 192115 TO 200000 |
| `cand-222d55315f21d765` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_to_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-2813877be408c22b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'type': 'nas:ARTCC', 'value': 'ZBW'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 192115 T... |
| `cand-2905f0aa1c7cda52` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T21:06:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:06 |
| `cand-2ea0e6a241a520b5` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | {'type': 'xsd:string', 'value': 'MEDIUM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 192115 T... |
| `cand-355d565d91817c46` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_area` | ZBW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZBW |
| `cand-36b8b48f3433e205` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | {'type': 'xsd:dateTime', 'value': '2026-05-19T19:21:15Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192115-200000 |
| `cand-37b8da991f9d6734` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T21:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192115-200000 |
| `cand-3defa7df9bf196f0` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192115-200000 |
| `cand-41fb01f32b8668bc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `uses_route` | BOSOX T303 HFD V3 CMK V623 KCDW KLDJ SAX | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KEWR KTEB KMMU >BOSOX T303 HFD V3 CMK V623 KCDW KLDJ SAX |
| `cand-44e73774f1c7c157` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | {'type': 'xsd:integer', 'value': 108} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-4aabcd317ebc7a66` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | {'type': 'xsd:string', 'value': 'RQD'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-5d8870c0c1872c9f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `must_comply_with` | altitude restrictions | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. |
| `cand-6b5454322e6b9812` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | {'type': 'nas:ARTCC', 'value': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 192115 T... |
| `cand-7cce48ddfb502345` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-801b2dce5b9df140` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-831feb1c6998b335` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteType` | {'type': 'xsd:string', 'value': 'ROUTE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-88756da0b2a83f32` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_facilities` | ZBW/ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZBW/ZNY |
| `cand-8fa09079f7e84bca` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 108 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-90e971656cd723f9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_maximum_altitude` | 10000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | JETS=10000 |
| `cand-967564155333ec7e` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteReason` | {'type': 'xsd:string', 'value': 'WEATHER'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 192115 T... |
| `cand-b3046168aeee3b99` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | {'type': 'xsd:dateTime', 'value': '2026-05-19T20:00:00Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192115-200000 |
| `cand-c3e85f77a332b09d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `uses_route` | BOSOX T303 MAD EEGOR PRENO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KLGA >BOSOX T303 MAD EEGOR PRENO |
| `cand-d3284c1ac70979ca` | `S1_llm_only` | `freeform_or_unmapped_fact` | `must_not_request` | higher altitude | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DO NOT REQUEST HIGHER ALTITUDE. |
| `cand-d40c9aba45f370ed` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | {'type': 'xsd:dateTime', 'value': '2026-05-19T21:06:00Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 21:06 |
| `cand-d4153188d033620a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `uses_route` | BURDY T358 SEY ARCAV ORCHA CCC V46 DPK JFK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KJFK >BURDY T358 SEY ARCAV ORCHA CCC V46 DPK JFK |
| `cand-dcdf6ca9966268e0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_traffic` | KBOS departures to KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB |
| `cand-e7127bf5fbb53ae2` | `S1_llm_only` | `freeform_or_unmapped_fact` | `uses_route` | BOSOX T303 MAD EEGOR | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KDXR >BOSOX T303 MAD EEGOR |
| `cand-ed85ecfe71d30247` | `S1_llm_only` | `freeform_or_unmapped_fact` | `uses_route` | BOSOX T303 MAD EEGOR | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KHPN >BOSOX T303 MAD EEGOR |
| `cand-ede10f35ad871569` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_named` | SERBOS_1_PARTIAL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL |
| `cand-f906cd015a6349c7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |

## ATCSCC-GOLD-012 / 2026-05-18:053

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=53
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: ATL_NO_JJEDI_PARTIAL CONSTRAINED AREA: ZTL REASON: EQUIPMENT INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 181400 TO 181800 PROBABILITY OF EXTENSION: MODERATE REMARKS: ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KJAX KATL >QUIWE LEAVI < OZZZI2 KMYR KSAV KSSI KEWN KFAY KILM KATL >RDU SHPRD LEAVI < OZZZI2 KOAJ KORF KPHF KRDU ZJX(-CAE -CHS -JAX KATL >AMORY Q110 DAWWN BEORN < -MYR -SAV -SSI) HOBTT3 ZMA KATL >AMORY Q110 DAWWN BEORN < HOBTT3 TMI ID: RRDCC502 EFFECTIVE TI...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-070bb8a738a572fb` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | KATL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL |
| `cand-0d0c926e5b5ef44f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T18:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181400-181800 |
| `cand-147a71f414c5d092` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-1fd57c52ffa6cf66` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_traffic` | ['KCAE', 'KCHS', 'KEWN', 'KFAY', 'KILM', 'KJAX', 'KMYR', 'KOAJ', 'KORF', 'KPHF', 'KRDU', 'KSAV', 'KSSI', 'ZJX', 'ZMA'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA |
| `cand-2354de6a1cd658ce` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-270c2629199be2a6` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-37ab9209c1d0d013` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 53 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-6c153b683ab65b56` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T13:52:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 13:52 |
| `cand-6fd3ce642858ee57` | `S1_llm_only` | `freeform_or_unmapped_fact` | `valid_during` | ETD 181400 TO 181800 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 181400 TO 181800 |
| `cand-70d210b15d8fd27b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteType` | ROUTE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-71488609082b1c9a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `modifies_routes_for_origin_destination` | [{'destination': 'KATL', 'origin': 'KCAE', 'route': 'QUIWE LEAVI'}, {'destination': 'KATL', 'origin': 'KCHS', 'route': 'QUIWE LEAVI'}, {'destination': 'KATL'... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KJAX KATL >QUIWE LEAVI < OZZZI2 KMYR KSAV KSSI KEWN KFAY KILM KATL >RDU SHPRD LEAVI < OZZZI2 KOAJ KORF KPHF KRDU ZJX(-CAE -CHS -JAX KATL >AMORY Q110 DAWWN BEORN < -MYR... |
| `cand-7e09e2ead1851f3b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T14:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181400-181800 |
| `cand-870e604de607b700` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T13:52:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 13:52 |
| `cand-89cf7870a7c3196d` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 53 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-8d79adff49473afb` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T18:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181400-181800 |
| `cand-8e8bd7a5407e7ad6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_facilities_included` | ['ZDC', 'ZJX', 'ZMA', 'ZTL'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL |
| `cand-92a3d04e4c0b693a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_effective_time` | 181400-181800 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181400-181800 |
| `cand-a92a8b79950d4060` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T14:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181400-181800 |
| `cand-a9f0b74bf965e04f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteReason` | EQUIPMENT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | REASON: EQUIPMENT |
| `cand-ab571d25f026f4ee` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is_named` | ATCSCC advisory traffic route restriction | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: ATL_NO_JJEDI_PARTIAL |
| `cand-b286772d11998492` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | equipment | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: EQUIPMENT |
| `cand-c2114210e82fde81` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-cd931378f46f69a0` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KAT... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-d6f677b5b27b699a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-de872189b2130046` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_departures_to` | KATL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL |
| `cand-ed64e47829d556c6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_area` | ZTL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZTL |
| `cand-fd70b5622e5a5522` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_tmi_id` | RRDCC502 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC502 |

## ATCSCC-GOLD-013 / 2026-05-18:124

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=124
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 31

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 182000 TO 190000 PROBABILITY OF EXTENSION: MODERATE REMARKS: REPLACES ADVZY 104. AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ZTL ADDED ROUTES: ORIG DEST ROUTE ---- ---- ----- ZTL KORD >VLKNN MEMFS RZC BUM IRK < BENKY6 KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK < KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK < BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK < BENKY6 ZME KORD >MEMFS RZC BUM IRK < B...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-18c089f5bb367e5a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `lists_facilities_included` | ZAU/ZJX/ZKC/ZMA/ZME/ZTL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-1e5281cbbc2a0755` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `initiativeComments` | REPLACES ADVZY 104. AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ZTL ADDED ROUTES: ORIG DEST ROUTE ---- ---- ----- ZTL KORD >VLKNN MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 104. AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ZTL ADDED ROUTES: ORIG DEST ROUTE ---- ---- ----- ZTL KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-1f9154bb16e8fb71` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T18:20:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-26689bb885e41e7b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-26fe193ee6d90c1b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-2a7dc6b29597d725` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | ZTL KORD >VLKNN MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZTL KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-340c75fd2e54a954` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_traffic` | KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-47ef1cf10bc89648` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | ZME KORD >MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZME KORD >MEMFS RZC BUM IRK |
| `cand-4c1d36bb9ec5ffe6` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-4ea57f3bf4d3664c` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-5313ec36c7e931e9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_associated_restrictions` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS: |
| `cand-584c9b0d7909bd6b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `replaces_advisory` | ADVZY 104 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REPLACES ADVZY 104. |
| `cand-5bce9fa2118bece7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_constrained_area` | ZID/ZOB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZID/ZOB |
| `cand-716aca1928030247` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-878c93e8d23c2913` | `S1_llm_only` | `freeform_or_unmapped_fact` | `valid_during` | ETD 182000 TO 190000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-8dede20490517700` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK |
| `cand-95bf0de7212f51cc` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `reRouteType` | ROUTE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-96ea8fb8f51a18c3` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T20:25:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:25 |
| `cand-9984fc7f591725f5` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:Airport KORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-b6e535f396013bc4` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `advisoryNumber` | 124 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-bc342f521179407e` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 124 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-cb3b53739a1e912d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_probability_of_extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-cd68e0ccba930f0a` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `implementationStatus` | RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-d810d3ab0086b645` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T19:00:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-d92e8b76aade4979` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_advisory_name` | SOUTHEAST_TO_ORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: SOUTHEAST_TO_ORD |
| `cand-e6d4ee7991f30214` | `S1_llm_only` | `freeform_or_unmapped_fact` | `notes_modification` | ZTL ADDED ROUTES | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: ZTL ADDED ROUTES: |
| `cand-e8a02588908ef065` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-e9650ef18626d64a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-ea5d3d7d263047fc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `contains_route` | KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK |
| `cand-eca6024bc6131e4a` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `reRouteReason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER |
| `cand-f8c20c532cc01b54` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T20:25:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |

## ATCSCC-GOLD-014 / 2026-05-18:104

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=104
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 31

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 182000 TO 190000 PROBABILITY OF EXTENSION: MODERATE REMARKS: AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK < KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK < BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK < BENKY6 ZME KORD >MEMFS RZC BUM IRK < BENKY6 TMI ID: RRDCC511 EFFECTIVE TIME: 182000-190000 SIGNATURE: 26/05...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-003286a339cbb1d8` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 104 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-0188660d7b012e9e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes traffic` | KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME departures to KORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-11e0c982717a31cf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has constrained area` | ZID/ZOB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB |
| `cand-134795ed329465c5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `routes to destination KORD via` | MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZME KORD >MEMFS RZC BUM IRK |
| `cand-13cd8da812de6f08` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-143782ac69f3150b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has flight status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-145ec06f266d5d0c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has identifier` | RRDCC511 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 TMI ID: RRDCC511 |
| `cand-1771639cc36b755f` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-18T19:18:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 19:18 |
| `cand-1a90b1b3dddf0ff6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `routes to destination KORD via` | JAWJA Q116 VLKNN MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK |
| `cand-21ede342adc52185` | `S1_llm_only` | `freeform_or_unmapped_fact` | `routes via` | BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK |
| `cand-33747a26ef2c3758` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-18T18:20:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-348a3fb61f3f9d30` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-34a72bcddf048c5c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has effective time` | 182000-190000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182000-190000 |
| `cand-377b7c0e8ae6340a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | KORD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-390d03ffc3d93593` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has remarks` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: AD-HOC ROUTING ASSOCIATED RESTRICTIONS |
| `cand-4b297589118a2f68` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has probability of extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-504a5107a6a72561` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-52b81223d7f091cf` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T20:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-6f479636ac20dfb2` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteType` | ROUTE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-7539c4c48d0e474a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | ZID/ZOB | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZID/ZOB |
| `cand-7705137f28a2c3af` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK < KJAX BENKY6 ZJX... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | REMARKS: AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK < KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -S... |
| `cand-8adc887a325515f8` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-18T19:18:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 19:18 |
| `cand-90091857cd4fb0d3` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 104 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-98bd4a86575fe8c9` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-18T19:00:00 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-a0da0153f20f66db` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteReason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-c0a64bcb4453c8eb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has included facilities` | ZAU/ZJX/ZKC/ZMA/ZME/ZTL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-c1f044fec1ebcd2a` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-c8e41bc3d3964c7c` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-d07757db56d32e9a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is valid during` | ETD 182000 TO 190000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-d3c0aa0fd7331741` | `S1_llm_only` | `freeform_or_unmapped_fact` | `routes to destination KORD via` | VLKNN MEMFS RZC BUM IRK | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-fc13d866fb23d881` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": 104, "atm:controlledNASelement": "nas:Airport", "atm:effectiveEndTime": "2026-05-18T19:00:00", "atm:effectiveStartTime": "2026-05-18T1... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD FACILITIES INCLUDED: ZAU/ZJX/... |

## ATCSCC-GOLD-015 / 2026-05-20:137

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=137
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 22

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: GREKI_1 CONSTRAINED AREA: ZNY REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES TO CYYZ/KBUF/KROC/KSYR FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202030 TO 210200 PROBABILITY OF EXTENSION: MODERATE REMARKS: FOR JETS ONLY AOB FL220 ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KEWR KJFK KLGA KBUF >GREKI JUDDS CAM SYR ROC KHPN KTEB EHMAN < KEWR KJFK KLGA CYYZ >GREKI JUDDS CAM Q822 GONZZ KHPN KTEB WOZEE < LINNG3 KEWR KJFK KLGA KSYR >GREKI JUDDS CAM < KHPN KTEB KEWR KJFK KLGA KROC >GREKI JUDDS CAM Q822 KHPN KTEB GONZZ < TMI ID: RRDCC137 EFFECTIVE TIME: 202030-210200...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-076e5137c2211d6f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `remark` | FOR JETS ONLY AOB FL220 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: FOR JETS ONLY AOB FL220 |
| `cand-2fa074849ad0bbfa` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 137 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-349dfca7c43d2a68` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": [{"evidence_text": "CONSTRAINED AREA: ZNY", "value": {"id": "ZNY", "type": "nas:ARTCC"}}], "atm:extensionProbability": [{"eviden... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-4f105c8531040423` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL", "value": 137}], "atm:controlledNASelement": [{"evidence_text": "NA... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-60ecf09ac663c7df` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has route modification` | {'destination': 'KBUF', 'origin': ['KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM SYR ROC KHPN KTEB EHMAN'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KEWR KJFK KLGA KBUF >GREKI JUDDS CAM SYR ROC KHPN KTEB EHMAN |
| `cand-7571e6f358425803` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies to destinations` | ['CYYZ', 'KBUF', 'KROC', 'KSYR'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES TO CYYZ/KBUF/KROC/KSYR |
| `cand-75a89507ab362664` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has route modification` | {'destination': 'KROC', 'origin': ['KHPN', 'KTEB', 'KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM Q822 KHPN KTEB GONZZ'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KHPN KTEB KEWR KJFK KLGA KROC >GREKI JUDDS CAM Q822 KHPN KTEB GONZZ |
| `cand-79cef125ebb321d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `probability of extension` | MODERATE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-7cc99458be815aff` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T02:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202030-210200 |
| `cand-7d8684e52826c6aa` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes traffic` | ['KEWR departures', 'KHPN departures', 'KJFK departures', 'KLGA departures', 'KTEB departures'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES |
| `cand-88f62e056de7f267` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202030-210200 |
| `cand-941293638a9be22c` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-9f17faf10042c10e` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T20:38:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 20:38 |
| `cand-a8d3edbef6d4025e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `facilities included` | ['CZY', 'ZBW', 'ZNY', 'ZOB'] | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB |
| `cand-ac2abfba5e91b4d9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has route modification` | {'destination': 'CYYZ', 'origin': ['KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM Q822 GONZZ KHPN KTEB WOZEE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KEWR KJFK KLGA CYYZ >GREKI JUDDS CAM Q822 GONZZ KHPN KTEB WOZEE |
| `cand-b45cb4495f5de209` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has route modification` | {'destination': 'KSYR', 'origin': ['KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | LINNG3 KEWR KJFK KLGA KSYR >GREKI JUDDS CAM |
| `cand-bc2c3ad7ff7d3f5f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `valid time window` | 202030 to 210200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 202030 TO 210200 |
| `cand-d7241352c385200e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-db7fb28af8dc0c3a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `effective time` | 202030-210200 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202030-210200 |
| `cand-e17e9c1599635cbd` | `S1_llm_only` | `freeform_or_unmapped_fact` | `tmi identifier` | RRDCC137 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC137 |
| `cand-e53dc8334305e4a3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is constrained area in` | ZNY | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: GREKI_1 CONSTRAINED AREA: ZNY |
| `cand-e76bf6924e551d4b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `flight status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |

## ATCSCC-GOLD-016 / 2026-05-20:078

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=78
- Candidate class: `ReRouteTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCLUDED: ZBW/ZDC/ZOB FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201315 TO 201830 PROBABILITY OF EXTENSION: MODERATE REMARKS: REPLACES ADVZY 056. FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE FLIGHT. IMPLEMENTED DUE TO SPECIAL OPERATIONS ASSOCIATED RESTRICTIONS: MODIFICATIONS: END TIME EXTENDED. ROUTES: ORIG DEST ROUTE ---- ---- ----- KBWI KDCA KIAD KBOS >JERES J211 LEONI WEVEL ELZ VIEEW ITH PONCT < JFUND2 TMI ID: RRDCC508 EFFECTIVE TIME: 201315-201830 SIGNATURE: 26/05/20...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1025436684a70caf` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_tmi_id'}` | {'label': 'RRDCC508', 'type': 'tmi_identifier'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | JFUND2 TMI ID: RRDCC508 |
| `cand-11d5b5033dd8e708` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'implemented_due_to'}` | {'label': 'SPECIAL OPERATIONS ASSOCIATED RESTRICTIONS', 'type': 'implementation_cause'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPLEMENTED DUE TO SPECIAL OPERATIONS ASSOCIATED RESTRICTIONS: |
| `cand-1385a73df72065b3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_modification'}` | {'label': 'END TIME EXTENDED', 'type': 'modification'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: END TIME EXTENDED. |
| `cand-29e03637c9206da4` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-315e9ffa07b6dfb8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'applies_to_flight_status'}` | {'label': 'ALL_FLIGHTS', 'type': 'flight_status'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-47fae381e2f5fda6` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `implementationStatus` | RQD | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-4ad3f23a65e388b0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_probability_of_extension'}` | {'label': 'MODERATE', 'type': 'extension_probability'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-4facfcd235286cd1` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-20T20:13:15Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | VALID: ETD 201315 TO 201830 |
| `cand-65944538c497d676` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'must_not_request_above'}` | {'label': 'FL220', 'type': 'altitude_limit'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE FLIGHT. |
| `cand-70bb5fe0fbf1da0a` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T13:15:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201315-201830 |
| `cand-7812cbb14393a36d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_reason'}` | {'label': 'OTHER', 'type': 'reason_category'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: OTHER |
| `cand-844308c3ce5665f7` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-20T20:18:30Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | VALID: ETD 201315 TO 201830 |
| `cand-927398af5097691b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteReason` | OTHER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS |
| `cand-9ed41dfbdb8bebfb` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_route'}` | {'label': 'KBWI KDCA KIAD KBOS >JERES J211 LEONI WEVEL ELZ VIEEW ITH PONCT', 'type': 'route_sequence'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ROUTES: ORIG DEST ROUTE ---- ---- ----- KBWI KDCA KIAD KBOS >JERES J211 LEONI WEVEL ELZ VIEEW ITH PONCT |
| `cand-a1a13de989b30b0a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_area'}` | {'label': 'ZBW', 'type': 'air_traffic_area'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW |
| `cand-a8045f48c346ce3e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_facilities_included'}` | {'label': 'ZBW/ZDC/ZOB', 'type': 'facility_group'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZBW/ZDC/ZOB |
| `cand-ac19da67097be827` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'replaces_advisory'}` | {'label': 'ADVZY 056', 'type': 'prior_advisory'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REPLACES ADVZY 056. |
| `cand-b180e43f3ebc6d11` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `extensionProbability` | MEDIUM | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCLUDED: ZBW/ZDC/ZOB FLIGHT STATUS: ALL_FLI... |
| `cand-b71df8bd1906acfd` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-20T15:56:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 15:56 |
| `cand-bf7ebd6b88aa3d52` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 78 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-c16e4f03876c57a3` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'must_comply_with'}` | {'label': 'ALTITUDE_RESTRICTIONS', 'type': 'operational_restriction'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. |
| `cand-c640120243b2451d` | `S0_rule_only` | `canonical_fact` | `extensionProbability` | MODERATE | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-cd86e2feb3341ade` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | nas:ARTCC/ZBW | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS |
| `cand-ce966079efebc246` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `reRouteType` | ROUTE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-da39b904e9e7a6fa` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'effective_time'}` | {'label': '201315-201830', 'type': 'effective_time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201315-201830 |
| `cand-e2a615872cda43f1` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `initiativeComments` | REPLACES ADVZY 056. FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE FLIGHT. IMPLEMENTED D... | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 056. FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE FLIGHT. IMPLEMENTED DUE TO SPECIAL OPERATIONS ASSOCIATED RESTRICTIONS: M... |
| `cand-e38d716c5dcbb0f5` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T18:30:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201315-201830 |
| `cand-ef8415cca4f36eca` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'valid_during'}` | {'label': '201315 TO 201830', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201315 TO 201830 |
| `cand-fd416b358f61ee4b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_traffic'}` | {'label': 'KBWI/KDCA/KIAD DEPARTURES TO KBOS', 'type': 'traffic_group'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS |

## ATCSCC-GOLD-017 / 2026-05-19:079

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=79
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0359Z CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0359Z PROGRAM RATE: 28/28/28/24/20/20/20/20 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME MAXIMUM DELAY: 106 AVERAGE DELAY: 54 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. EFFECTIVE TIME: 191854-200459 SIGNATURE: 26/05/19 18:55 FAA.gov Home \| Privacy Policy \| Web Pol...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0322e7c86c6a50ac` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_canadian_departure_arpts_included'}` | {'label': 'NONE'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-06de3134b9a05d97` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T04:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191854-200459 |
| `cand-16fc3fbe92029117` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_impacting_condition'}` | {'label': 'STAFFING'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-1810b63e04346257` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_effective_time'}` | {'label': '191854-200459'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191854-200459 |
| `cand-1c38d1c3e2a825d1` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `initiativeComments` | BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. |
| `cand-2502128243d6d123` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | {"name": "BNA", "type": "nas:Airport"} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM |
| `cand-2e039e93f0874d25` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'delay_assignment_table_applies_to'}` | {'label': 'ZME'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-30a530cdd4403781` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. | `{"repaired_accepted": 1}` | `{}` | COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. |
| `cand-3144ff4b5e07e19c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'applies_to_scope'}` | {'label': 'ZME'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-37feae132dd998c8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_estimated_arrival_window'}` | {'label': '19/2030Z - 20/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0359Z |
| `cand-3ad54f638dfbfe5b` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T18:55:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 18:55 |
| `cand-3d4be95b65e7201c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_delay_assignment_mode'}` | {'label': 'UDP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-3dad173d39e6845b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_cumulative_program_period'}` | {'label': '19/2030Z - 20/0359Z'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0359Z |
| `cand-3dd654bde84a4ca9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_flights'}` | {'label': 'ALL CONTIGUOUS US DEP DEP'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-5038b9a7bff28a78` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 79 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM |
| `cand-56fd8a8116f2773c` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0359Z CUMULATIVE PROGRAM PERIOD... |
| `cand-5bfc2f764bc80ade` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_average_delay_minutes'}` | {'label': '54'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 54 |
| `cand-bdca69a44dc4c158` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_maximum_delay_minutes'}` | {'label': '106'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 106 |
| `cand-bdd7c0ef8b01d784` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-d9113b2c0b6c635d` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-e601e1c54cd08c6f` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_ctl_element'}` | {'label': 'APT ADL'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL |
| `cand-f6187c3e99a832be` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_staffing_comment'}` | {'label': 'BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45.'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | STAFFING COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. |
| `cand-f69669631039ffc7` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-f86a0f1c587823e7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_program_rate_pattern'}` | {'label': '28/28/28/24/20/20/20/20'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 28/28/28/24/20/20/20/20 |
| `cand-fa585d27da6a7b85` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T18:54:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191854-200459 |

## ATCSCC-GOLD-018 / 2026-05-19:074

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=74
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0459Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0459Z ANTICIPATED PROGRAM RATE: 28/18/18/20/20/20/20/20/20 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME ANTICIPATED MAXIMUM DELAY: 175 ANTICIPATED AVERAGE DELAY: 109 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0619c39ee2f987e8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'effective_time_window'}` | {'label': '191840-191959', 'type': 'effective_time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191840-191959 |
| `cand-0a62d2e065d9ad21` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'applies_to'}` | {'label': 'ZME', 'type': 'air_traffic_control_center'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-1acc7540475d6c7f` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-20eb22714e6c4b91` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'estimated_for_time_window'}` | {'label': '19/2030Z - 20/0459Z', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0459Z |
| `cand-3552919944bfbfe9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'announces_program'}` | {'label': 'CDM Proposed Ground Delay Program', 'type': 'traffic_management_program'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-3fe2f5ae6212eac8` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_anticipated_program_rate_sequence'}` | {'label': '28/18/18/20/20/20/20/20/20', 'type': 'rate_sequence'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 28/18/18/20/20/20/20/20/20 |
| `cand-4562f13c052a9147` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_element_type'}` | {'label': 'APT ADL', 'type': 'element_type'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-56ab0422ae66e405` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_anticipated_average_delay_minutes'}` | {'label': '109', 'type': 'duration_minutes'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 109 |
| `cand-5fd3c948d0031fae` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T18:40:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191840-191959 |
| `cand-6c26868dfb25a473` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_flights'}` | {'label': 'ALL CONTIGUOUS US DEP', 'type': 'flight_scope'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-778759268fbecb82` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `controlledNASelement` | BNA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0459Z ANTICIPATED CUMU... |
| `cand-7b1535ec577984e6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'scheduled_at'}` | {'label': '1850Z', 'type': 'zulu_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONFERENCE AT 1850Z |
| `cand-81689fd2f24c9704` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-19T18:41:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 18:41 |
| `cand-81e6ef870697a088` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_anticipated_cumulative_program_period'}` | {'label': '19/2030Z - 20/0459Z', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0459Z |
| `cand-87adf0faad9e6dc4` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-8e1d00868bb41a8e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'uses_delay_assignment_mode'}` | {'label': 'UDP', 'type': 'delay_assignment_mode'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-94c7be30077362bd` | `S2_llm_schema_slice` | `property_bundle` | `property_bundle` | {"atm:controlledNASelement": {"evidence_text": "CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z", "value": "nas:Airport"}, "atm:effectiveEndTime": {"evide... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-986b6c2563da626a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'includes_canadian_departure_airports'}` | {'label': 'NONE', 'type': 'airport_list'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-9c0e213c62f6ea57` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T19:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191840-191959 |
| `cand-a779fface9bdb479` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'will_be_in_configuration'}` | {'label': 'TRACAB configuration', 'type': 'airport_configuration'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. |
| `cand-aaf105750a721755` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_anticipated_maximum_delay_minutes'}` | {'label': '175', 'type': 'duration_minutes'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 175 |
| `cand-ac5b18f3df6c7f86` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 74 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-bc8ab3df96887374` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'is_controlled_by'}` | {'label': 'BNA Element', 'type': 'control_element'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-c0a28e9bcc3ed318` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_departure_scope'}` | {'label': '(ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP', 'type': 'departure_scope'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-db698dff5340eec5` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_impacting_condition'}` | {'label': 'STAFFING', 'type': 'operational_condition'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-f1ca9f648e36d4f8` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES MUST BE RECEIVED BY: 19/1850Z | `{"repaired_accepted": 1}` | `{}` | COMMENTS: BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES MUST BE RECEIVED BY: 19/1850Z |
| `cand-f2dbab2cb607623c` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-f3859b7df9277294` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'must_be_received_by'}` | {'label': '19/1850Z', 'type': 'deadline_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 19/1850Z |
| `cand-f8cdc03ec34a53d7` | `S1_llm_only` | `freeform_or_unmapped_fact` | `'has_adl_time'}` | {'label': '1836Z', 'type': 'zulu_time'} | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1836Z |

## ATCSCC-GOLD-019 / 2026-05-15:067

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=67
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1945Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z PROGRAM RATE: 32 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1000 CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME MAXIMUM DELAY: 59 AVERAGE DELAY: 29 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 EFFECTIVE TIME: 151949-160129 SIGNATURE: 26/05/15 19:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-098768609f9bbcdb` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveStartTime` | 2026-05-15T22:00:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-0c7c9589102c4337` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `controlledNASelement` | BNA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1945Z |
| `cand-15b0078de29a8399` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_effective_time` | 151949-160129 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151949-160129 |
| `cand-15dfd0a4e8e98fcc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_maximum_delay` | 59 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 59 |
| `cand-1bc2930f7fc181b7` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-2e86da07e4b4df13` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_impacting_condition` | STAFFING | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-31776c8923d37881` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T01:29:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151949-160129 |
| `cand-3590197aa4173305` | `S1_llm_only` | `freeform_or_unmapped_fact` | `sets_delay_assignment_mode` | UDP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-3c6097da2b5aa722` | `S3_llm_schema_slice_validator_repair` | `property_bundle` | `property_bundle` | {"atm:advisoryNumber": [{"evidence_text": "ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM", "value": 67}], "atm:controlledNASelement": [{"evide... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` |  |
| `cand-3dddffeecd66489b` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_estimated_coverage_window` | 15/2200Z - 16/0029Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-495faedde2dcd22b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `effectiveEndTime` | 2026-05-16T00:29:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-4e759cfbe77a4ff9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_average_delay` | 29 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 29 |
| `cand-64d9e6ca99f8933e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_cumulative_program_period` | 15/2200Z - 16/0029Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z |
| `cand-6849fef2d3783da0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `states_canadian_departure_airports_included` | NONE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-6f9eefae9781427a` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes_staffing_comments` | ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-73deb98123567b12` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-763be96945560557` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies_delay_assignment_table_to` | ZME | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-77960c1181f6a212` | `S1_llm_only` | `freeform_or_unmapped_fact` | `defines_departure_scope` | 1000 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: 1000 |
| `cand-79437fc413bb62be` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 67 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-8337cae1114c67c8` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesAirportType` | contiguous us dep | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-9354915bcb9cc03b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `issuedTime` | 2026-05-15T19:50:00Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | SIGNATURE: 26/05/15 19:50 |
| `cand-96fec7f4922e1d06` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `departureScope` | _:airportSpec1 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-a215df6e37ad3ab0` | `S1_llm_only` | `freeform_or_unmapped_fact` | `declares_advisory_type` | APT ADL TIME | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL TIME: 1945Z |
| `cand-a7e0a0adf22a2d29` | `S1_llm_only` | `freeform_or_unmapped_fact` | `sets_program_rate` | 32 FLT | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 32 FLT |
| `cand-b8c6db60835e8e2b` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `advisoryNumber` | 67 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-be4552892c347273` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-cc845a160df7a9e2` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-ce2bacbf99b6f3e4` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T19:50:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 19:50 |
| `cand-e0910e5d97943bf4` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T19:49:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151949-160129 |
| `cand-e2e1b51a54732953` | `S1_llm_only` | `freeform_or_unmapped_fact` | `identifies_control_element` | BNA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-f2c85dd82de94fb8` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-f650b1e1ce390783` | `S1_llm_only` | `freeform_or_unmapped_fact` | `defines_flight_inclusion_scope` | ALL CONTIGUOUS US DEP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-f6e0b66454d46854` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `includesAirport` | CANADIAN DEP ARPTS INCLUDED: NONE | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |

## ATCSCC-GOLD-020 / 2026-05-15:084

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=84
- Candidate class: `GroundDelayProgramTMI`
- Current status: `pending_manual_gold_annotation`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2254Z - 16/0659Z CUMULATIVE PROGRAM PERIOD: 15/1500Z - 16/0659Z PROGRAM RATE: 36/36/36/30/30/32/36/36/36 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC DELAY ASSIGNMENT TABLE APPLIES TO: ZOA MAXIMUM DELAY: 758 AVERAGE DELAY: 70 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER EFFECTIVE TIME: 15...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-067eba2df276de84` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is stated as` | 2254Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2254Z |
| `cand-0c19b3b7724e9ef9` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes` | (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-1791764c26f6ed40` | `S1_llm_only` | `freeform_or_unmapped_fact` | `covers` | 15/1500Z - 16/0659Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 15/1500Z - 16/0659Z |
| `cand-1c9fbd64edfb9a4e` | `S1_llm_only` | `freeform_or_unmapped_fact` | `announces` | CDM ground delay program | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-25fb28efc2d003d6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `describe` | ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER |
| `cand-283cae11f2576ee6` | `S1_llm_only` | `freeform_or_unmapped_fact` | `covers` | 15/2254Z - 16/0659Z | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 15/2254Z - 16/0659Z |
| `cand-35f759aaabe626fe` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes` | ALL CONTIGUOUS US DEP DEP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-3a713bc3a3c78da8` | `S0_rule_only` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-4a3a70d34316a6dc` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is identified as` | SFO | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-5122dab5802bdade` | `S0_rule_only` | `canonical_fact` | `initiativeComments` | ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER |
| `cand-5791db8b75e0e2ef` | `S0_rule_only` | `canonical_fact` | `impactingCondition` | staffing | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-5c165069e9c287e6` | `S3_llm_schema_slice_validator_repair` | `schema_shaped_object` | `advisoryNumber` | 84 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2254Z - 16/0659Z CUMULATIVE PROGRAM PERIOD... |
| `cand-75ca97869473708c` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is` | 70 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 70 |
| `cand-77db9d373b50988d` | `S0_rule_only` | `canonical_fact` | `issuedTime` | 2026-05-15T23:00:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 23:00 |
| `cand-9d2e579ad61bb461` | `S1_llm_only` | `freeform_or_unmapped_fact` | `has element type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-9e72d36c5c784398` | `S1_llm_only` | `freeform_or_unmapped_fact` | `includes` | CYEG CYVR CYYC | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-a4537e5ad39bba55` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is` | STAFFING | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER |
| `cand-a91635d36b6cfeff` | `S1_llm_only` | `freeform_or_unmapped_fact` | `lists` | 36/36/36/30/30/32/36/36/36 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 36/36/36/30/30/32/36/36/36 |
| `cand-ab99cd90298f562f` | `S0_rule_only` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T07:59:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152258-160759 |
| `cand-cc325bf70ce9223d` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is` | 758 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 758 |
| `cand-cde58a33bd009818` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is set to` | UDP | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-d6a81890eec02aca` | `S1_llm_only` | `freeform_or_unmapped_fact` | `applies to` | ZOA | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZOA |
| `cand-dc03049d0083610c` | `S0_rule_only` | `canonical_fact` | `impactingConditionMessage` | STAFFING / STAFFING | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-dc42f630b2d08dd3` | `S0_rule_only` | `canonical_fact` | `advisoryNumber` | 84 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-f14315cfd8d4244b` | `S0_rule_only` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T22:58:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152258-160759 |
| `cand-fa21b3a67ade4403` | `S1_llm_only` | `freeform_or_unmapped_fact` | `is` | 152258-160759 | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 152258-160759 |
