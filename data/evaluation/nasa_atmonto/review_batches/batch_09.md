# NASA ATMONTO Gold Review batch_09

- Samples: `ATCSCC-GOLD-081` to `ATCSCC-GOLD-090`
- Records: 10
- Candidate clusters: 278

## Batch Checklist

- [ ] Read every source text excerpt and URL when needed.
- [ ] Mark semantically valid candidate facts.
- [ ] Mark semantically invalid candidate fact IDs.
- [ ] Add missing gold facts with evidence text.
- [ ] Copy final decisions into `atcscc_gold_annotation_template.jsonl`.

## ATCSCC-GOLD-081 / 2026-05-18:023

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=23
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 37

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LAS ELEMENT TYPE: APT ADL TIME: 0615Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 18/0615Z - 18/0759Z CUMULATIVE PROGRAM PERIOD: 18/0056Z - 18/0759Z PROGRAM RATE: 32 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1400 CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZLA MAXIMUM DELAY: 893 AVERAGE DELAY: 232 IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. EFFECTIVE TIME: 180619-180859 SIGNATURE: 26/05/18 06:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word V...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04a547a35ef4d6dc` | `S1_llm_only` | `canonical_fact` | `has_canadian_departure_airports_included` | NONE | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-06c5594d180b69ca` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 23 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM |
| `cand-0d648a2139a2036c` | `S1_llm_only` | `canonical_fact` | `has_advisory_title` | CDM GROUND DELAY PROGRAM | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM |
| `cand-0fedaf28ac0713cd` | `S1_llm_only` | `canonical_fact` | `has_control_element` | LAS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS |
| `cand-2847c80570af6975` | `S1_llm_only` | `canonical_fact` | `has_maximum_delay` | 893 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 893 |
| `cand-2eb2abf6d47b16b5` | `S1_llm_only` | `canonical_fact` | `has_cumulative_program_period` | 18/0056Z - 18/0759Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 18/0056Z - 18/0759Z |
| `cand-340f6b286dd3be8f` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T06:20:00Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM ... IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-395a78176e7a3642` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:APT | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-48c4a9385266b33b` | `S1_llm_only` | `canonical_fact` | `has_delay_assignment_table_applies_to` | ZLA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZLA |
| `cand-48e4d89db3600120` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM ... IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-4d2188d661510e03` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingConditionMessage` | WEATHER / WIND | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / WIND |
| `cand-566adec6fa4c664f` | `S1_llm_only` | `canonical_fact` | `has_delay_assignment_mode` | UDP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-5ab9bc038dce9692` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather / wind | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / WIND |
| `cand-5b36a4ff93ed6fb5` | `S1_llm_only` | `canonical_fact` | `has_departure_scope` | 1400 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SCOPE: 1400 |
| `cand-636039e1af7538d9` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:NONE | `{"repaired_accepted": 1}` | `{}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-67718b49fb0b21da` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T08:59:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180619-180859 |
| `cand-6f6df5c201c13820` | `S1_llm_only` | `canonical_fact` | `has_average_delay` | 232 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 232 |
| `cand-70d4bdd4a3f244c2` | `S1_llm_only` | `canonical_fact` | `has_included_departure_scope` | ALL CONTIGUOUS US DEP | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCL: ALL CONTIGUOUS US DEP |
| `cand-814e82d963453a93` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T06:19:00Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM ... IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-83a46a9280ee6762` | `S1_llm_only` | `canonical_fact` | `has_estimated_arrival_window` | 18/0615Z - 18/0759Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 18/0615Z - 18/0759Z |
| `cand-890455a7d72267a5` | `S1_llm_only` | `canonical_fact` | `has_adl_time` | 0615Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 0615Z |
| `cand-893cae2a721a23ef` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T06:20:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 06:20 |
| `cand-92120e86710e14e0` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-9f46e3a5c655e194` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T08:59:00Z | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM ... IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-a2208356d57c3244` | `S1_llm_only` | `canonical_fact` | `has_impacting_condition` | WEATHER / WIND | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / WIND |
| `cand-adc6c444b776d90e` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM ... IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-b2b8ea5169f82519` | `S1_llm_only` | `canonical_fact` | `has_comment` | ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-bad0fba9140eba4a` | `S1_llm_only` | `canonical_fact` | `has_control_element_type` | APT ADL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-c551a39da05884d5` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADL | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-c8ba88d21b5f42b2` | `S1_llm_only` | `canonical_fact` | `issued_by` | FAA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FAA Home |
| `cand-d460a6c50a36a26e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T06:19:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180619-180859 |
| `cand-e049650a641cfe04` | `S1_llm_only` | `canonical_fact` | `has_program_rate` | 32 FLT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 32 FLT |
| `cand-e0f23f97f998feb4` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 23 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM ... IMPACTING CONDITION: WEATHER / WIND COMMENTS: ARR 01L / DEP 01R/01L, BY STATUS, MED POP UP, GROUND STOP CANCELLED. LOOK FOR NEW EDCTS. |
| `cand-eae817c0a399f68e` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 180619-180859 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180619-180859 |
| `cand-f7921ff9723ec760` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `impactingCondition` | weather | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / WIND |
| `cand-fa451639c54a8036` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: LAS |
| `cand-fd13cc3321fa65e4` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | LAS | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: LAS ELEMENT TYPE: APT ADL TIME: 0615Z |

## ATCSCC-GOLD-082 / 2026-05-20:145

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=145
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 51

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000 PROBABILITY OF EXTENSION: LOW REMARKS: REPLACES ADVZY 143 ASSOCIATED RESTRICTIONS: MODIFICATIONS: ARRIVALCHANGED TO JOVEM/HERBZ ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- ZDV >LAA ZLC >JNC HBU PUB LAA ZLC >HVE J28 PUB LAA ZOA >MLF J28 PUB LAA TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KDAL LAA MMB FILGO HYDES < HERBZ2 KDFW LAA MMB MDANO < JOVEM6 TMI ID: RRDCC525 EFFECTIVE TIME: 202...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1122886ef965481b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 145 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-16dfe9dfc9245d13` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLC | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA |
| `cand-1cc42d89e5af9561` | `S1_llm_only` | `canonical_fact` | `origin_route_segments` | ZDV >LAA; ZLC >JNC HBU PUB LAA; ZLC >HVE J28 PUB LAA; ZOA >MLF J28 PUB LAA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- ZDV >LAA ZLC >JNC HBU PUB LAA ZLC >HVE J28 PUB LAA ZOA >MLF J28 PUB LAA |
| `cand-1dcb436450a28946` | `S1_llm_only` | `canonical_fact` | `has_valid_window` | ETD 202100 TO 210000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 202100 TO 210000 |
| `cand-1eac0fe8eae0bc35` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA |
| `cand-25bef3ace268d801` | `S1_llm_only` | `canonical_fact` | `has_probability_of_extension` | LOW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-25dd12c1c903c5e0` | `S1_llm_only` | `canonical_fact` | `destination_route_for` | KDAL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- KDAL LAA MMB FILGO HYDES |
| `cand-28833365f928f392` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 145 | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-37f5725e2886cd75` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteType` | ROUTE | `{"repaired_accepted": 1}` | `{}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |
| `cand-3a06a470ba5f4c5e` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteType` | ROUTE | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-3c126a05812b6848` | `S1_llm_only` | `canonical_fact` | `replaces_advisory` | ADVZY 143 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REPLACES ADVZY 143 |
| `cand-3c584877321433e7` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:00:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-4286b4e8755bfee2` | `S1_llm_only` | `canonical_fact` | `has_flight_status` | ALL_FLIGHTS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-43d1248120b2a183` | `S1_llm_only` | `canonical_fact` | `arrival_route_name` | JOVEM6 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | JOVEM6 TMI ID: RRDCC525 |
| `cand-528a3835e2a40269` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | RQD | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-64d4eef1bd1f339e` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | LOW | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-65276ac32675ad12` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `reRouteReason` | WEATHER | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-666391f7e48934b9` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | LOW | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-67b0d7f5bd3d5596` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T20:21:00Z | `{"repaired_accepted": 1}` | `{}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |
| `cand-6b9932106b455c3c` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `extensionProbability` | LOW | `{"repaired_accepted": 1}` | `{}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |
| `cand-6de40b880c82e8c2` | `S1_llm_only` | `canonical_fact` | `has_name` | DFW_NO_DOGS_HEAD_PARTIAL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL |
| `cand-6eef3f6ffe37dac3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T21:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202100-210000 |
| `cand-75b4766ce3eacf9c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-21T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202100-210000 |
| `cand-832696c283c6be18` | `S1_llm_only` | `canonical_fact` | `has_constrained_area` | ZAB | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZAB |
| `cand-90976919924c3e31` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | RQD | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-91e6fcefc8953c52` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | ROUTE | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-91f59e25ccc361a6` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T21:00:00Z | `{"repaired_accepted": 1}` | `{}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |
| `cand-94be9d43e7010b47` | `S1_llm_only` | `canonical_fact` | `destination_route_segments` | LAA MMB FILGO HYDES | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KDAL LAA MMB FILGO HYDES |
| `cand-97523e19ac52f693` | `S1b_llm_canonicalized` | `canonical_fact` | `impactingCondition` | weather | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-99fe857766b195c1` | `S1_llm_only` | `canonical_fact` | `effective_time` | 202100-210000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202100-210000 |
| `cand-9ee6992399e70b63` | `S1_llm_only` | `canonical_fact` | `includes_facilities` | ZDV/ZFW/ZKC/ZLC/ZOA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA |
| `cand-9f51490c3a790884` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T21:12:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:12 |
| `cand-a0e3e127d1f2f37a` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-a119526c9ada474f` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {"@type": "nas:Airport", "evidence_text": "CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZD... | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000 PROBABILITY OF EXTENSION: LOW |
| `cand-a221de3b0f785954` | `S2_llm_schema_slice` | `canonical_fact` | `allowedRoute` | {"@type": "atm:ReRouteSegment", "atm:implementationStatus": "RQD", "atm:reRouteType": "ROUTE", "evidence_text": "ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS -... | `{"repaired_accepted": 2}` | `{}` | ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- ----------------------- ZDV >LAA ZLC >JNC HBU PUB LAA ZLC >HVE J28 PUB LAA ZOA >MLF J28 PUB LAA TO: DEST ROUTE - DESTINATION SEGMENTS ---- ---------------------------- K... |
| `cand-a558fb46bc4835ee` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | REPLACES ADVZY 143 ASSOCIATED RESTRICTIONS: MODIFICATIONS: ARRIVALCHANGED TO JOVEM/HERBZ ROUTES: FROM: ORIG ROUTE - ORIGIN SEGMENTS ---- --------------------... | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-ae897c775bc33d90` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA |
| `cand-b6a2eecf6fe967d9` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `extensionProbability` | LOW | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: LOW |
| `cand-bafc647b6b2c926e` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `initiativeComments` | REPLACES ADVZY 143; MODIFICATIONS: ARRIVALCHANGED TO JOVEM/HERBZ ROUTES | `{"repaired_accepted": 1}` | `{}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |
| `cand-bb8b54b2369365bf` | `S1_llm_only` | `canonical_fact` | `includes_traffic` | ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW |
| `cand-bc2c305c89ff8836` | `S1_llm_only` | `canonical_fact` | `has_modification` | ARRIVALCHANGED TO JOVEM/HERBZ | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: ARRIVALCHANGED TO JOVEM/HERBZ |
| `cand-c28ab5e084ea74f5` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T21:00:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-c97e924cfa5d42b7` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA |
| `cand-da7bcea322aab0fa` | `S1_llm_only` | `canonical_fact` | `destination_route_for` | KDFW | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | HERBZ2 KDFW LAA MMB MDANO |
| `cand-e55b73bd9ec51e3d` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-20T21:12:00Z | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-e9005dc8ccf1e4f8` | `S1_llm_only` | `canonical_fact` | `has_reason` | WEATHER | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-eb4cdeb3795dc8e0` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |
| `cand-eb8adaece695e707` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOA | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA |
| `cand-f10006da3061b675` | `S1_llm_only` | `canonical_fact` | `destination_route_segments` | LAA MMB MDANO | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | HERBZ2 KDFW LAA MMB MDANO |
| `cand-f44ad1a2feea5ff8` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 145 | `{"repaired_accepted": 1}` | `{}` | REPLACES ADVZY 143 |
| `cand-ffb293c25b88d04a` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `implementationStatus` | RQD | `{"repaired_accepted": 1}` | `{}` | NAME: DFW_NO_DOGS_HEAD_PARTIAL CONSTRAINED AREA: ZAB REASON: WEATHER INCLUDE TRAFFIC: ZDV/ZLC/ZOA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZDV/ZFW/ZKC/ZLC/ZOA FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202100 TO 210000... |

## ATCSCC-GOLD-083 / 2026-05-20:016

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=16
- Candidate class: `GroundStopTMI`
- Current status: `reviewed`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA REMARKS: DAL AND SUBS GS CX. EFFECTIVE TIME: 200052-200200 SIGNATURE: 26/05/20 00:52 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-12ae48ce67c06682` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:52:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200052-200200 |
| `cand-1ed5b5ffc465b0f5` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 16 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-2a83e8ddedcf5db1` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-38f76ca4c0d28cb9` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-20T00:52:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-3cc591c711d9e7b4` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-4b256368ea715446` | `S2_llm_schema_slice` | `canonical_fact` | `extensionProbability` | NONE | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-4ed9d5a733937e7c` | `S1_llm_only` | `canonical_fact` | `'LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS'}` | {'label': 'ground stop cancellation for DAL and subsidiaries', 'text': 'LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-526f96105bdfd5cb` | `S1_llm_only` | `canonical_fact` | `'05/20/2026'}` | {'label': '2026-05-20', 'text': '05/20/2026'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-5b0bc4c27c60d7e6` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-5f56e012290c2d50` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | DAL AND SUBS GS CX. | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-60600f39b67b1d6f` | `S2_llm_schema_slice` | `canonical_fact` | `withinARTCC` | ZNY | `{"repaired_accepted": 2}` | `{}` | DESTINATION AIRPORT: LGA AND JFK |
| `cand-6f9bf4ed630ff433` | `S1_llm_only` | `canonical_fact` | `'20/0050 - 20/0130'}` | {'label': 'event time window', 'text': '20/0050 - 20/0130'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/0050 - 20/0130 |
| `cand-9b746ed1110235c7` | `S2_llm_schema_slice` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-a9a184899df24153` | `S1_llm_only` | `canonical_fact` | `'200052-200200'}` | {'label': 'effective time window', 'text': '200052-200200'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200052-200200 |
| `cand-af97dfcc33e30d46` | `S3_llm_schema_slice_validator_repair` | `freeform_or_unmapped_fact` | `unmapped_payload` |  | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-b1bd1861f54c67f2` | `S1_llm_only` | `canonical_fact` | `'LGA AND JFK'}` | {'label': 'LGA and JFK', 'text': 'LGA AND JFK'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DESTINATION AIRPORT: LGA AND JFK |
| `cand-bbc29b2bfa06bae6` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:00:00 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, Z... |
| `cand-d01eed29cbdb034c` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 16 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-d2a39e6fd8bab368` | `S1_llm_only` | `canonical_fact` | `'ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA'}` | {'label': 'released facilities list', 'text': 'ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RELEASED FACILITIES: ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA |
| `cand-eb197e85d719967a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-20T02:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200052-200200 |
| `cand-ed84a9ec32b55b05` | `S1_llm_only` | `canonical_fact` | `'ZNY'}` | {'label': 'ZNY', 'text': 'ZNY'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-f76295299b384250` | `S1_llm_only` | `canonical_fact` | `'DAL AND SUBS GS CX.'}` | {'label': 'ground stop cancellation for DAL and subsidiaries', 'text': 'DAL AND SUBS GS CX.'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: DAL AND SUBS GS CX. |
| `cand-f92cdeb325d0f5bf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-20T00:52:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:52 |

## ATCSCC-GOLD-084 / 2026-05-17:017

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=17
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 31

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI MESSAGE: EVENT TIME: 17/1900 - 18/0200 CONSTRAINED FACILITIES: ZNY THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT, CUSTOMERS ARE ENCOURAGED TO FILE PUBLISHED CDR'S AND NRP PROCEDURES AROUND KNOWN FORECASTED WEATHER. THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. SWAP STATEMENT: **MORNING FORECAST** SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0efa2ccd4ccebd00` | `S1_llm_only` | `canonical_fact` | `states_planning_purpose_only` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-12dfcfcfa0e9ccd7` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | WEATHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-137fdebd730d2038` | `S1_llm_only` | `canonical_fact` | `recommends_published_CDR_and_NRP_use_when_no_route_advisories` | file published CDR's and NRP procedures around known forecasted weather | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT, CUSTOMERS ARE ENCOURAGED TO FILE PUBLISHED CDR'S AND NRP PROCEDURES AROUND KNOWN FORECASTED WEATHER. |
| `cand-154a3478fd4312dc` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. | `{"repaired_accepted": 1}` | `{}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-2a2d8867cd93dd12` | `S1_llm_only` | `canonical_fact` | `may_have_additional_reroutes_for_effected_airways_outside_ZNY` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDITIONAL DEPARTURE REROUTES MAY BE POSSIBLE FOR IMPACTS TO EFFECTED AIRWAYS OUTSIDE ZNY. |
| `cand-32a80b991ec164db` | `S1_llm_only` | `canonical_fact` | `names_destinations_to_file_normal_routes` | ATL/CLT/MDW/ORD | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. |
| `cand-37523eb62517f90e` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. | `{"repaired_accepted": 1}` | `{}` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. |
| `cand-41e3047895aa39b8` | `S1_llm_only` | `canonical_fact` | `possible_active_time` | AFT ( XXX )Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY HOTLINE POSSIBLE AFT ( XXX )Z: 540-359-3200 PIN #2778 |
| `cand-4692e1d165f39990` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 17 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-48356baef1c9b000` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-17T11:40:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171140-180230 |
| `cand-5305cbb7917807c2` | `S1_llm_only` | `canonical_fact` | `expects_impact_area` | ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. |
| `cand-617eb6f00e0c7283` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-67ea915c6eed7c08` | `S1_llm_only` | `canonical_fact` | `identifies_weather_avoidance_plans_as_possible` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) |
| `cand-6b9ad235923f168a` | `S1_llm_only` | `canonical_fact` | `will_provide_reroutes_or_CDRs_as_necessary` | True | `{"rejected_schema": 3}` | `{"unknown_object_class": 3, "unknown_predicate": 3, "unknown_subject_class": 3}` | POSSIBLE REROUTES / CDR'S WILL BE PROVIDED AS NECESSARY. |
| `cand-74f4b3cf95df1872` | `S1_llm_only` | `canonical_fact` | `encourages_compliance_with` | all ATCSCC route advisories | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. |
| `cand-763cec57cc5e093d` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). | `{"repaired_accepted": 1}` | `{}` | SWAP STATEMENT: **MORNING FORECAST** SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). |
| `cand-77c3e973c5e43eae` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-7c9c88f92df2a1ae` | `S1_llm_only` | `canonical_fact` | `impact_status` | not_expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DITCH IMPACTS ARE: NOT EXPECTED |
| `cand-8a871f260b7c132b` | `S1_llm_only` | `canonical_fact` | `states_impacts_to_j6_q75_and_dc_metros` | possible | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTS TO J6-Q75 & DC METROS PSBL. |
| `cand-9fef01d12ee6215d` | `S1_llm_only` | `canonical_fact` | `identifies_constrained_facility` | ZNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-ab3ef1e8545a2aa6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T02:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171140-180230 |
| `cand-af4c6cfce126bcbc` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | MISCELLANEOUS | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-b16fb95f8f8202ba` | `S1_llm_only` | `canonical_fact` | `describes_swap_as_possible` | True | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SWAP IS POSSIBLE |
| `cand-c4682ce485b65159` | `S1_llm_only` | `canonical_fact` | `impact_status` | not_expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AZEZU-PAEPR-HANRI ( L453-Y493 ) IMPACTS ARE: NOT EXPECTED |
| `cand-c8e2840256a89dbb` | `S1_llm_only` | `canonical_fact` | `impact_status` | not_expected | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INTERNATIONAL DEPARTURES ( EAST GATES ) IMPACTS ARE: NOT EXPECTED |
| `cand-cbf228d4e71f2f8c` | `S1_llm_only` | `canonical_fact` | `effective_time` | 171140-180230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171140-180230 |
| `cand-d2e2d5fbbe95228f` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | nas:Airport | `{"repaired_accepted": 1}` | `{}` | THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. |
| `cand-e387a6420f36dea8` | `S1_llm_only` | `canonical_fact` | `will_provide_alternate_routes_to_destinations` | ATL/CLT/MDW/ORD | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. |
| `cand-f2026a1c01b83167` | `S1_llm_only` | `canonical_fact` | `specifies_area_and_time` | ZNY area today/ after ( 19Z ) | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). |
| `cand-f2602070fad5a455` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `implementationStatus` | FYI | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _FYI |
| `cand-f4acd7d8dd0dfc99` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-17T11:40:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 11:40 |

## ATCSCC-GOLD-085 / 2026-05-19:009

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=9
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 190306 WSI DDS:190307 VA ADVISORY DTG: 20260519/0306Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0004 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/493 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 19/0250Z EST VA CLD: SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07740 - N0000 W07751 - N0004 W07748 MOV NW 15KT FCST VA CLD +6HR: 19/0900Z SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07740 - N0000 W07751 - N0004 W07748 FCST VA CLD +12HR: 19/1500Z SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07739 - N0000 W07751 - N0004 W07748 FCST VA CLD +18HR: 19/2100Z...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1d14064bc6c09720` | `S1_llm_only` | `canonical_fact` | `'has source area'}` | {'label': 'Ecuador', 'type': 'country'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-26e8d0d5940288ce` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 9 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-2bca347bf460f031` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-19T03:07:00Z | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/19 03:07 |
| `cand-32e21f75e105dad6` | `S1_llm_only` | `canonical_fact` | `'has no change forecast for'}` | {'label': 'next 18 hours', 'type': 'time_window'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-3728dd683a1bd243` | `S1_llm_only` | `canonical_fact` | `'likely continue'}` | {'label': 'recent activity', 'type': 'activity'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-39693846926ba1f2` | `S1_llm_only` | `canonical_fact` | `'has source elevation'}` | {'label': '11686 ft AMSL', 'type': 'elevation'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-50f434e6ad5e90d2` | `S1_llm_only` | `canonical_fact` | `'moves northwest at'}` | {'label': '15 kt', 'type': 'speed'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 15KT |
| `cand-8fc329eade16102e` | `S1_llm_only` | `canonical_fact` | `'is observed from'}` | {'label': 'surface to flight level 140', 'type': 'vertical_extent'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 |
| `cand-90962e52f41ddc70` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-19T03:06:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:07 |
| `cand-9db736f91d3d6579` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-a0d2c106d37e230f` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-afc9a12f8588e128` | `S1_llm_only` | `canonical_fact` | `'is not detected due to'}` | {'label': 'weather clouds in summit area', 'type': 'weather_condition'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-c7f7211b37c4263f` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-ee2a7bfbb43f43ca` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - REVENTADOR | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-efa7f75ac8283fa1` | `S1_llm_only` | `canonical_fact` | `'reports eruption details'}` | {'label': 'ongoing volcanic ash emissions', 'type': 'eruption_state'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING VA EMS |
| `cand-f7400c7e86cdb4ff` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 9 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 009 |
| `cand-ffd38ef41f1ed0e4` | `S1_llm_only` | `canonical_fact` | `'names volcano'}` | {'label': 'Reventador', 'type': 'volcano'} | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |

## ATCSCC-GOLD-086 / 2026-05-16:046

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=46
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY MESSAGE: FVAK21 PAWU 161536 WSI DDS:161538 VA ADVISORY DTG: 20260516/1536Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5558 E16035 AREA: KAMCHATKA SOURCE ELEV: 9455 FT AMSL ADVISORY NR: 2026/001 INFO SOURCE: TOKYO VAAC. ERUPTION DETAILS: NOT PROVIDED OBS VA DTG: NOT PROVIDED OBS VA CLD: NOT PROVIDED FCST VA CLD +6HR: 16/2100Z NOT PROVIDED FCST VA CLD +12HR: 17/0300Z NOT PROVIDED FCST VA CLD +18HR: 17/0900Z NOT PROVIDED RMK: PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. ...GATLING EFFECTIVE TIME: 160000-160000 SIGNATURE: 26/05/16 15:38 FAA.gov Home \|...

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-020a115c95d31ef5` | `S1_llm_only` | `canonical_fact` | `names_volcano` | BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: BEZYMIANNY |
| `cand-078f37d973872f0a` | `S1_llm_only` | `canonical_fact` | `states_eruption_details` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: NOT PROVIDED |
| `cand-0b363d1a5694336b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-16T15:36:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 15:38 |
| `cand-0cdcf31b7acb54c8` | `S1_llm_only` | `canonical_fact` | `has_position` | N5558 E16035 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5558 E16035 |
| `cand-1dedd5ac05eb5cbd` | `S1_llm_only` | `canonical_fact` | `has_subject_line` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-1e8ea5c7f33dbfb7` | `S1_llm_only` | `canonical_fact` | `states_forecast_volcanic_ash_cloud_plus_12_hours` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 17/0300Z NOT PROVIDED |
| `cand-1f2d5d450281345e` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 46 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-264c9f98bffef555` | `S1_llm_only` | `canonical_fact` | `has_effective_time_window` | 160000-160000 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160000-160000 |
| `cand-3df3714097b3d05e` | `S1_llm_only` | `canonical_fact` | `includes_remarks` | PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. |
| `cand-5a4b9a6c9be24e60` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T16:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-796af776698e8cd3` | `S1_llm_only` | `canonical_fact` | `has_information_source` | TOKYO VAAC | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: TOKYO VAAC. |
| `cand-7d4176d90c5e29fc` | `S1_llm_only` | `canonical_fact` | `reports_issued_datetime` | 20260516/1536Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260516/1536Z |
| `cand-867d45fb43613d03` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-16T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-8fb83001bff4211a` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 46 | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/001 |
| `cand-9021ae04186b74ab` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 46 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 046 |
| `cand-905feca8a9f50edb` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T15:38:00Z | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 15:38 |
| `cand-9745407ebe8135a7` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T16:00:00Z | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-9a03559eed29a0a2` | `S1_llm_only` | `canonical_fact` | `states_forecast_volcanic_ash_cloud_plus_18_hours` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 17/0900Z NOT PROVIDED |
| `cand-bb064abb171c665f` | `S1_llm_only` | `canonical_fact` | `cites_advisory_number` | 2026/001 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/001 |
| `cand-c5d488d378858983` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T00:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-d0dbcdf471b89412` | `S1_llm_only` | `canonical_fact` | `has_source_elevation` | 9455 FT AMSL | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 9455 FT AMSL |
| `cand-d86486a4e50b44e3` | `S1_llm_only` | `canonical_fact` | `states_observed_volcanic_ash_cloud` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: NOT PROVIDED |
| `cand-e1c7fd94debae5f5` | `S1_llm_only` | `canonical_fact` | `is_in_area` | KAMCHATKA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA |
| `cand-e88bc7c2ec2db28b` | `S1_llm_only` | `canonical_fact` | `states_forecast_volcanic_ash_cloud_plus_6_hours` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/2100Z NOT PROVIDED |
| `cand-eebb40b237360edc` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-f2027cdf9be56ce8` | `S1_llm_only` | `canonical_fact` | `states_observed_volcanic_ash_datetime` | NOT PROVIDED | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: NOT PROVIDED |

## ATCSCC-GOLD-087 / 2026-05-18:107

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=107
- Candidate class: `TrafficManagementInitiative`
- Current status: `reviewed`
- Candidate clusters: 23

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. EFFECTIVE TIME: 181933-190230 SIGNATURE: 26/05/18 19:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08642cd4ac4e12d4` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `issuedTime` | 2026-05-18T19:33:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 19:33 |
| `cand-0c2dfced8c665d9a` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | DENVER AIRPORT | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-1602c895f66ad6fb` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T02:30:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30... |
| `cand-1cc15e7191c79c0d` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. |
| `cand-2653f921c60e0622` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-38ce9629e5ec291d` | `S1_llm_only` | `canonical_fact` | `states_expected_delay_for` | DENVER AIRPORT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-4b3eddb8230dc7b3` | `S1_llm_only` | `canonical_fact` | `describes_event_time` | 18/2045 - 19/0200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/2045 - 19/0200 |
| `cand-54f4ed5c5d267c84` | `S1_llm_only` | `canonical_fact` | `states_affected_departure_airports_scope` | departure airports within the first tier facilities | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES |
| `cand-55116fa027f5c714` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-19T02:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181933-190230 |
| `cand-614c3525e309a517` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:FIRST | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES |
| `cand-6ac709f53bc51830` | `S1_llm_only` | `canonical_fact` | `applies_to_center` | ZDV | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-6e8f89641f2f8189` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | ZDV users can expect TBFM / CALL-FOR-RELEASE scheduling delays to Denver Airport of 30 to 45 minutes from departure airports within the first tier facilities. | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30... |
| `cand-7bbd9d3d59da59dd` | `S1_llm_only` | `canonical_fact` | `identifies_constrained_facilities` | ZDV | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-887f7319dc183b29` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T19:33:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30... |
| `cand-91700a75a88dc84d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T19:33:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 19:33 |
| `cand-9399bf0008fcfc51` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T19:33:00 | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30... |
| `cand-9e5edede9f38e4c2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T19:33:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181933-190230 |
| `cand-a79a2dc81d0cb144` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:TIER | `{"repaired_accepted": 1}` | `{}` | FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES |
| `cand-b580893c453f2d39` | `S1_llm_only` | `canonical_fact` | `has_advisory_type` | DEN airport scheduling delays | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-bf1db667bb3d6424` | `S1_llm_only` | `canonical_fact` | `states_effective_time` | 181933-190230 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181933-190230 |
| `cand-db10d1cfb5781f3c` | `S1_llm_only` | `canonical_fact` | `states_delay_type` | TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-ec55f7cd15ea3061` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 107 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-f6cfd4e254a9485c` | `S1_llm_only` | `canonical_fact` | `states_delay_duration_range` | 30 TO 45 MINUTES | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |

## ATCSCC-GOLD-088 / 2026-05-18:021

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=21
- Candidate class: `GroundDelayProgramTMI`
- Current status: `reviewed`
- Candidate clusters: 26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EFFECTIVE TIME: 180507-180945 SIGNATURE: 26/05/18 05:07 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-13e40f2e41302060` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T09:45:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-23f22c9b0381ebd7` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-18T05:07:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-29a66fccccd701dd` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 21 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-3efe823de3e1ec57` | `S1_llm_only` | `canonical_fact` | `element_type` | APT | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-47f9add13d7fc6c6` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | OBJECTIVES MET | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-5574c0597082b73b` | `S1_llm_only` | `canonical_fact` | `advisory_time` | 0503Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-60f5bb49e3d14ecf` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 21 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-70eec77c13ad0f16` | `S1b_llm_canonicalized` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-746e81e209a25fec` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | OBJECTIVES MET | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-8950bba896410d4b` | `S1_llm_only` | `canonical_fact` | `announced_advisory_area` | SFO/ZOA | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-8e1da0077d9d3634` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T05:07:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180507-180945 |
| `cand-9ea24e3df8c233a6` | `S1_llm_only` | `canonical_fact` | `ground_delay_program_status` | CNX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-a70627d46a9738c1` | `S1_llm_only` | `canonical_fact` | `named_airport_element` | SFO | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-ab3bd42808a8cf0f` | `S1_llm_only` | `canonical_fact` | `comment` | OBJECTIVES MET | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-b84942381cf3d2f0` | `S2_llm_schema_slice` | `canonical_fact` | `impactingCondition` | other | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-bfee977774ad0d92` | `S1_llm_only` | `canonical_fact` | `ground_delay_program_period` | 18/0503Z - 18/0845Z | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-c152438b1f916c03` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-c5a2fe167d9ad0bb` | `S1_llm_only` | `canonical_fact` | `announced_advisory_topic` | CDM GROUND DELAY PROGRAM CNX | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-db306c36ca46a977` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-18T05:07:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 05:07 |
| `cand-ddb905fd1e845152` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-18T05:07:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-e0d1107d83bbd155` | `S1_llm_only` | `canonical_fact` | `instruction` | DISREGARD EDCTS FOR DEST SFO | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-e5a27602ea762e5e` | `S1_llm_only` | `canonical_fact` | `effective_interval` | 180507-180945 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180507-180945 |
| `cand-f050227a1791a55d` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | SFO | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EF... |
| `cand-f4357847596acd43` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `initiativeComments` | OBJECTIVES MET | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: OBJECTIVES MET |
| `cand-f5f8bd554146d954` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-18T09:45:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180507-180945 |
| `cand-fe2ef636381314d5` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `canonical_fact` | `controlledNASelement` | SFO | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |

## ATCSCC-GOLD-089 / 2026-05-16:018

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=18
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION MESSAGE: EVENT TIME: 16/0915 - 17/0200 THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. EFFECTIVE TIME: 160909-170200 SIGNATURE: 26/05/16 09:09 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-112c742427a7bb1a` | `S1_llm_only` | `canonical_fact` | `runs from` | 16/0915 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-2180ab82d6e2b4de` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T09:09:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160909-170200 |
| `cand-2187d7c3ede64a5b` | `S1_llm_only` | `canonical_fact` | `should include` | call sign | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-29d584dc630f730f` | `S1_llm_only` | `canonical_fact` | `announces issue request page activation` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-2ba28bf90fdfe6ef` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-16T09:09:00 | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 09:09 |
| `cand-38b10d04444616dc` | `S1_llm_only` | `canonical_fact` | `should include` | position of flight | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-4ac5c791e5d25323` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-16T09:15:00 | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-5a200bfb6ff9aac2` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELI... | `{"repaired_accepted": 1}` | `{}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-696f9b21b7875a7c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-16T09:09:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 09:09 |
| `cand-718ae46f7899f3b3` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. | `{"repaired_accepted": 1}` | `{}` | THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. |
| `cand-908ed24cc012aaae` | `S1_llm_only` | `canonical_fact` | `should include` | type of assistance requested | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-914cadbbf58abf85` | `S1_llm_only` | `canonical_fact` | `should send` | request messages to the page for resolution | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. |
| `cand-94e474a342fa80e3` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 18 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-961deb74700c1f07` | `S1_llm_only` | `canonical_fact` | `purpose` | to eliminate any misinterpretation | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-b571f87b97c6d347` | `S1_llm_only` | `canonical_fact` | `has advisory identifier` | 018 DCC 05/16/2026 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-c52fb2626696a34a` | `S1_llm_only` | `canonical_fact` | `should include` | category of issue | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. |
| `cand-d2c1d4da2957005d` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T02:00:00 | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-d523bcaee34d7f1b` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 18 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-d61e7bba6e3d5e3c` | `S1_llm_only` | `canonical_fact` | `starts at` | 160909 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160909-170200 |
| `cand-dc03fb5f688b97b8` | `S1_llm_only` | `canonical_fact` | `ends at` | 170200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160909-170200 |
| `cand-dc9f0d89c9f2860a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-17T02:00:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160909-170200 |
| `cand-e1f2971163f70e9f` | `S1_llm_only` | `canonical_fact` | `status` | now open | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. |
| `cand-e8c7da8442b0ec2a` | `S1_llm_only` | `canonical_fact` | `runs until` | 17/0200 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-eb601e0cc92a74e0` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. | `{"repaired_accepted": 1}` | `{}` | WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. |
| `cand-f6a7e276c2743530` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |

## ATCSCC-GOLD-090 / 2026-05-15:061

- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=61
- Candidate class: `ReRouteTMI`
- Current status: `reviewed`
- Candidate clusters: 19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Review actions:

- [ ] valid facts selected
- [ ] invalid candidate fact IDs selected
- [ ] missing facts added
- [ ] rejected facts adjudicated if applicable

| Candidate | Systems | Kind | Predicate | Value/Object | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0703fc3843d29ecf` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteReason` | OTHER | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-12ff7c8e36f83676` | `S2_llm_schema_slice` | `canonical_fact` | `reRouteType` | FCA | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-225b32cfd279489f` | `S2_llm_schema_slice` | `canonical_fact` | `issuedTime` | 2026-05-15T18:49:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-394a9427d3385086` | `S1_llm_only` | `canonical_fact` | `has_effective_time` | 151849-152030 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151849-152030 |
| `cand-3b247360808b1922` | `S1_llm_only` | `canonical_fact` | `has_status` | cancelled | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. |
| `cand-48a8209359defff1` | `S2_llm_schema_slice` | `canonical_fact` | `initiativeComments` | FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-4ded2e61eaaf84d8` | `S2_llm_schema_slice` | `canonical_fact` | `controlledNASelement` | {"evidence_text": "FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS:", "type": "nas:Airport"} | `{"repaired_accepted": 1}` | `{}` | FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: |
| `cand-5706831032f1e78f` | `S1_llm_only` | `canonical_fact` | `message_type` | reroute cancellation | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION |
| `cand-6804f514149409cb` | `S1_llm_only` | `canonical_fact` | `cancels_reference_advisory` | ADVZY 024 | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: |
| `cand-6b1b80bd23a8554d` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `canonical_fact` | `advisoryNumber` | 61 | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION |
| `cand-8794711dbce0e9b2` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-89a2ea6c2625f5f5` | `S2_llm_schema_slice` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T18:49:00Z | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-8dce73f0301551d6` | `S2_llm_schema_slice` | `canonical_fact` | `advisoryNumber` | 61 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-a4f275de0537c1bb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `issuedTime` | 2026-05-15T18:49:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 18:49 |
| `cand-b000cf7eca091ea4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151849-152030 |
| `cand-c7c0e885c4098f37` | `S2_llm_schema_slice` | `canonical_fact` | `implementationStatus` | FYI | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-cc0de7da6c373558` | `S3_llm_schema_slice_validator_repair` | `canonical_fact` | `advisoryNumber` | 61 | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 |
| `cand-cdc623c8aed2bc19` | `S1b_llm_canonicalized` | `canonical_fact` | `advisoryNumber` | 61 | `{"repaired_accepted": 1}` | `{}` | REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: |
| `cand-e9329b80d227d255` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `canonical_fact` | `effectiveStartTime` | 2026-05-15T18:49:00Z | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151849-152030 |
