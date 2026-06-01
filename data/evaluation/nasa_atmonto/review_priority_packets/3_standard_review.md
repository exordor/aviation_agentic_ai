# NASA ATMONTO Gold Review Priority Packet: 3_standard_review

- Label: Standard source review
- Records: 49
- Estimated review time: 746 minutes
- Candidate clusters: 1158
- Cross-system clusters: 1158
- Rejected facts: 0

## Packet Checklist

- [ ] Read the source excerpt and open the source URL when the excerpt is insufficient.
- [ ] Copy source-supported S0 IDs into `valid_candidate_fact_ids`.
- [ ] Copy source-supported schema-valid S1-S3 IDs into `valid_cross_system_fact_ids`.
- [ ] Add corrected or missing facts manually when no candidate is source-correct.
- [ ] Complete rejected-fact adjudications when present.

## ATCSCC-GOLD-064 / 2026-05-19:112

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=65, est=19 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 32
- Cross-system clusters: 32
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=112

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 192120-200230 SIGNATURE: 26/05/19 21:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-010ab42774bbf8fb` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-05a6f577a08157ea` | `S2_llm_schema_slice` | `initiativeComments` | THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPO... | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-11eed613d7076da2` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | DFW | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-064:fact-02-fe5359c5b55a` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISOR... |
| `cand-13ffe95ea458b2a6` | `S2_llm_schema_slice` | `controlledNASelement` | {"evidence_text": "DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT", "type": "nas:Airport"} | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT |
| `cand-1d974e8f4b2da93d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZFW |
| `cand-1e94f9a93c4fe9ba` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T02:30:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-30e06911240494c4` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 112 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-064:fact-01-538472620b5c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISOR... |
| `cand-385bb1c9ea626c71` | `S2_llm_schema_slice` | `initiativeComments` | THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPO... | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-3ae00cb227cdedfa` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T21:20:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-4ac641321bd61580` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-4d6ce92e121bd728` | `S1_llm_only` | `'has_advisory_title'}` | {'label': 'DFW Airport Arrival Delays'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS |
| `cand-54c1219971853847` | `S1_llm_only` | `'extends_timeframe_of'}` | {'label': 'Advisory 039'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISORY 039. |
| `cand-54e863e4b9f0b28f` | `S1_llm_only` | `'maximum_delay_duration'}` | {'label': 'up to 30 minutes'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-61ffcd5f78004b8b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T21:20:00Z | `fact-b77c0e667afad0de` | `fact-b77c0e667afad0de` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192120-200230 |
| `cand-665825838606905c` | `S1_llm_only` | `'effective_time'}` | {'label': '192120-200230'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192120-200230 |
| `cand-6a506f9b00c90973` | `S2_llm_schema_slice` | `advisoryNumber` | 112 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-8b88d0c6e2408406` | `S1_llm_only` | `'can_expect'}` | {'label': 'airborne holding'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-9287ba4ec9f9f0b0` | `S1_llm_only` | `'caused_by'}` | {'label': 'thunderstorms'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-99c9633f3fbdacdb` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T21:21:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-9dbdb90f8e86f630` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T21:20:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-a380d84e290a5e71` | `S1b_llm_canonicalized` | `impactingCondition` | thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-a3c10a2fd68bed7f` | `S1_llm_only` | `'event_time_window'}` | {'label': '19/2100 - 20/0200'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/2100 - 20/0200 |
| `cand-a71aed38e80843f2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T21:20:00Z | `fact-f5612fb17b2d43f9` | `fact-f5612fb17b2d43f9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:20 |
| `cand-bc35e0a525acd656` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-064:fact-03-a03b6df507b3` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/2100 - 20/0200 CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTENDS THE TIMEFRAME FOR ADVISOR... |
| `cand-c1f440b35c20bb63` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T02:30:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-c95c1f06670c56fa` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T21:21:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-cbd4698efcfd9a81` | `S1_llm_only` | `'constrained_facility'}` | {'label': 'ZFW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZFW |
| `cand-cd609d316645bd0a` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 112 | `fact-386c998630f14b53` | `S1b_llm_canonicalized:2026-05-19:112:fact-b5149db5fee4, fact-386c998630f14b53` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS |
| `cand-ce3395676511f54b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `fact-c378abe391c00451` | `fact-c378abe391c00451` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192120-200230 |
| `cand-d537b2f2ddb2134f` | `S2_llm_schema_slice` | `controlledNASelement` | {"evidence_text": "DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT", "type": "nas:Airport"} | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | DFW AIRPORT ARRIVAL DELAYS; ... INTO THE DALLAS FORT WORTH AIRPORT |
| `cand-ed4cd0a3dbf58c77` | `S2_llm_schema_slice` | `advisoryNumber` | 112 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS ... EFFECTIVE TIME: 192120-200230 ... SIGNATURE: 26/05/19 21:20 ... CONSTRAINED FACILITIES: ZFW THIS ADVISORY EXTE... |
| `cand-fac8ec9190417fee` | `S1_llm_only` | `'can_expect'}` | {'label': 'arrival delays'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE DALLAS FORT WORTH AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |

## ATCSCC-GOLD-073 / 2026-05-20:006

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=65, est=19 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 32
- Cross-system clusters: 32
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=6

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 11735 / 587 / 170 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 15134 / 662 / 219 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION COMMENTS: EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b044c4876578a80` | `S1_llm_only` | `'states_probability_of_extension'}` | {'class': 'extension_probability', 'label': 'MEDIUM'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-0b2d405223ca8ca0` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T00:15:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-07-ee87dd717342` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-0ffb3bd1152b8351` | `S2_llm_schema_slice` | `impactingCondition` | runway | `` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-03-7d14dca88316` | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION COMMENTS: |
| `cand-14e7b2827f8319b4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:20:00Z | `fact-bb287e67bf78fd07` | `fact-bb287e67bf78fd07` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-26202b36718cb883` | `S2_llm_schema_slice` | `controlledNASelement` | DFW | `` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-01-f1485274045c` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-2e46c09b43eceffa` | `S1_llm_only` | `'reports_new_total_maximum_average_delays'}` | {'class': 'delay_measurement', 'label': '15134 / 662 / 219'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 15134 / 662 / 219 |
| `cand-3150f5e1f4ad0359` | `S1_llm_only` | `'names_controlled_element'}` | {'class': 'controlled_element', 'label': 'DFW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DFW |
| `cand-37b85ccd388751fa` | `S2_llm_schema_slice` | `initiativeComments` | RWY-TAXI / CONSTRUCTION | `` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-04-40e1f0e7ba22` | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION COMMENTS: |
| `cand-50f7b778c58ecec9` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-5ccce3a674f15115` | `S1b_llm_canonicalized:2026-05-20:006:fact-bcfe1e4b7526, S2_llm_schema_slice:ATCSCC-GOLD-073:fact-02-5f4c5789f3bb, fact-5ccce3a674f15115` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-59fde377b7696bdd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T00:21:00Z | `fact-d3788a983bac048a` | `fact-d3788a983bac048a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:21 |
| `cand-5fa531f35b4ac3a9` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-64e06df212e412a3` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T02:15:00Z | `fact-c07cff8f5064b92f` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-08-20059c88556b, fact-c07cff8f5064b92f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-66e5d080f875473a` | `S1_llm_only` | `'reports_previous_total_maximum_average_delays'}` | {'class': 'delay_measurement', 'label': '11735 / 587 / 170'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 11735 / 587 / 170 |
| `cand-6c0157f4b34cc93c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-37da5da96c88f747` | `fact-37da5da96c88f747` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200020-200215 SIGNATURE: 26/05/20 00:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-6db5930eafc8ee45` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DFW | `fact-8970acf8443198a8` | `fact-8970acf8443198a8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DFW |
| `cand-73ec9cc8a93ad35a` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | DFW | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-073:fact-01-f59bccf6f3fc` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DFW |
| `cand-7e7546cee392c110` | `S1_llm_only` | `'states_cumulative_program_period'}` | {'class': 'time_interval', 'label': '19/2100Z - 20/0359Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 19/2100Z - 20/0359Z |
| `cand-890cd8cd862db4f1` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-05-5147456f7dcc` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-aedb827cc874337d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-aee06c0e54467e2a` | `S1b_llm_canonicalized` | `impactingCondition` | rwy-taxi / construction | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION |
| `cand-c6b22601be6b7f74` | `S1_llm_only` | `'gives_effective_time_window'}` | {'class': 'effective_time_window', 'label': '200020-200215'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200020-200215 |
| `cand-ca1f4f1898b0df87` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-073:fact-02-daf7d70619ff` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DFW ELEMENT TYPE: APT ADL TIME: 0019Z GROUND STOP PERIOD: 20/0000Z - 20/0115Z CUMULATIVE PROGRAM PERIOD... |
| `cand-d02dfecd4f137bb3` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-d107f2ae1f4635b6` | `S1_llm_only` | `'identifies_impacting_condition'}` | {'class': 'impacting_condition', 'label': 'RWY-TAXI / CONSTRUCTION'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: RWY-TAXI / CONSTRUCTION |
| `cand-d3534ec8ecc0467f` | `S1_llm_only` | `'announces_ground_stop_period'}` | {'class': 'time_interval', 'label': '20/0000Z - 20/0115Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/0000Z - 20/0115Z |
| `cand-d98908e0e1a56600` | `S2_llm_schema_slice` | `departureScope` | {"class": "atm:AirportSpec", "properties": {"atm:withinARTCC": [{"evidence_text": "DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-09-732d06be3a75` | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-da8b94d887897753` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 6 | `fact-c60561ecf3330996` | `fact-c60561ecf3330996` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP |
| `cand-dc1b2540226e5186` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-dd10f2b507df027f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-f285afa06fcdaf40` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-073:fact-06-53e5ebc35f18` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200020-200215 |
| `cand-f6a9fbb335086b86` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'facility_group', 'label': 'ZHU ZFW ZKC ZME ZAB'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZHU ZFW ZKC ZME ZAB |
| `cand-f8e3e98b201dccbd` | `S1_llm_only` | `'specifies_element_type'}` | {'class': 'element_type', 'label': 'APT ADL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |

## ATCSCC-GOLD-074 / 2026-05-14:073

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=65, est=19 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 32
- Cross-system clusters: 32
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=73

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 141857 WSI DDS:141858 VA ADVISORY DTG: 20260514/1857Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/562 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: FRQ VA EMS OBS VA DTG: 14/1830Z OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 FCST VA CLD +18HR: 15/1230Z SFC/F...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0429a57fb256e737` | `S1_llm_only` | `has_vertical_extent` | SFC/FL150 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-0e50e9dc8ea8c899` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T18:59:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-074:fact-03-407da75924ca` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 18:59 |
| `cand-152e8ad5f455ed54` | `S1_llm_only` | `has_position` | N1428 W09052 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-1ab04e3383d8c8a2` | `S1_llm_only` | `observation_time` | 14/1830Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 14/1830Z |
| `cand-1af384f0f11b4ffe` | `S1_llm_only` | `reports_event_type` | volcanic activity bulletin | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-21498afb668a17bd` | `S1_llm_only` | `has_forecast_polygon` | N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-236c76e780014a4f` | `S1_llm_only` | `references_information_sources` | GOES-19, WEBCAM, NWP MODELS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. |
| `cand-2b29b06e67f919b7` | `S1_llm_only` | `has_reported_polygon` | N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-34688e067cb56f5e` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-14T14:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-074:fact-04-2513a8f8258a` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-3b01664e72aeb0ae` | `S1_llm_only` | `forecast_vertical_extent` | SFC/FL150 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-599d5ae2dc66fc14` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-14T14:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-074:fact-05-02beda6f93d4` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-5a811f1daea39870` | `S1_llm_only` | `forecast_vertical_extent` | SFC/FL150 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-5aef29c501c088f6` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 73 | `fact-b3a4c87b5276cf58` | `S1b_llm_canonicalized:2026-05-14:073:fact-e437727546af, S2_llm_schema_slice:ATCSCC-GOLD-074:fact-01-75f36b018fbe, fact-b3a4c87b5276cf58` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-5e6abcc9e6cd775b` | `S1_llm_only` | `states_forecast_winds` | SW AND W WINDS THRU T+18HRS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDL FCST SW AND W WINDS THRU T+18HRS. |
| `cand-6348a208e23a9f78` | `S1_llm_only` | `states_ash_clouds_disperse_slowly_and_reach_distance` | appx 8 NM fm summit | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA CLDS SLOWLY DISPERSED W REACHING APPX 8 NM FM SUMMIT. |
| `cand-66f94cda0934a8bb` | `S1_llm_only` | `names_volcano` | FUEGO | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-7616c8f0d5009365` | `S1_llm_only` | `has_forecast_polygon` | N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-7815a5a347130a97` | `S1_llm_only` | `forecast_time` | 15/1230Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |
| `cand-a030ff50aef3cdf0` | `S1_llm_only` | `has_advisory_identifier` | ATCSCC ADVZY 073 DCC 05/14/2026 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-b34de0768593a96c` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `` | `S2_llm_schema_slice:ATCSCC-GOLD-074:fact-02-0d4d7ef5904e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-b719bf763f0c498d` | `S1_llm_only` | `has_eruption_details` | FRQ VA EMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: FRQ VA EMS |
| `cand-ba5122c0db00cbb7` | `S1_llm_only` | `located_in_area` | GUATEMALA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-bb9daa9b906ee8d7` | `S1_llm_only` | `forecast_time` | 15/0030Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/0030Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09105 - N1426 W09107 - N1429 W09053 |
| `cand-bd9131016e75ddab` | `S1_llm_only` | `movement_direction_and_speed` | W 5KT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 N1431 W09100 - N1428 W09052 - N1427 W09053 - N1428 W09101 - N1431 W09100 MOV W 5KT |
| `cand-bef5fc5d2bed4ac0` | `S1_llm_only` | `has_source_elevation` | 12346 FT AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-c5512d00622ad7db` | `S1_llm_only` | `has_forecast_polygon` | N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |
| `cand-ce500204dde4bb58` | `S1_llm_only` | `forecast_time` | 15/0630Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/0630Z SFC/FL150 N1428 W09052 - N1426 W09052 - N1422 W09108 - N1428 W09109 - N1428 W09052 |
| `cand-ddb667efef17ffc1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `fact-7a82728438207b9a` | `fact-7a82728438207b9a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-e04fd891011ab2d8` | `S1_llm_only` | `states_volcanic_ash_emissions_observed_in` | sat and webcam | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: FRQ VA EMS OBSD IN SAT AND WEBCAM. |
| `cand-e98731719a55f7ba` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T18:57:00Z | `fact-28d267e3c353e3c6` | `fact-28d267e3c353e3c6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 18:59 |
| `cand-f34c3d06e78fe7ec` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `fact-8e5c4018edbb061a` | `fact-8e5c4018edbb061a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-f7f2e52dbefe9338` | `S1_llm_only` | `forecast_vertical_extent` | SFC/FL150 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/1230Z SFC/FL150 N1429 W09052 - N1426 W09051 - N1419 W09106 - N1424 W09108 - N1429 W09052 |

## ATCSCC-GOLD-038 / 2026-05-20:115

- Batch: `batch_04`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_04.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=63, est=19 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 31
- Cross-system clusters: 31
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=115

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z CUMULATIVE PROGRAM PERIOD: 20/1700Z - 21/0359Z PROGRAM RATE: 18/18/22/24/24/24/24 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1425 CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB DELAY ASSIGNMENT TABLE APPLIES TO: ZNY MAXIMUM DELAY: 272 AVERAGE DELAY: 97 IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. EFFECTIVE TIME: 201857-210459 SIGNATURE: 26/05/20 18:59 FAA.gov Home \| Privacy Policy \| Web Policies &...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02181c8d7e8be602` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'delay_assignment_mode', 'text': 'UDP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-036242b9822104d0` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'rate_sequence', 'text': '18/18/22/24/24/24/24'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 18/18/22/24/24/24/24 |
| `cand-06191c699e48f767` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-ac07b61c0a8e61fd` | `fact-ac07b61c0a8e61fd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1f0d5767284eb7a0` | `S2_llm_schema_slice` | `advisoryNumber` | 115 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-038:fact-01-716f6a749db5` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/21... |
| `cand-21403bfb60101e69` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'airport_and_center_area', 'text': 'LGA/ZNY'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM |
| `cand-252adb2e56b05cfa` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'airport', 'text': 'LGA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LGA |
| `cand-3a0f65cd5bdd7080` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'comment', 'text': 'ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS.'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. |
| `cand-4ab1468cb55b37c9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T18:57:00Z | `fact-7e98c5ebdae11fb4` | `fact-7e98c5ebdae11fb4` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201857-210459 |
| `cand-4c0ab9883a4f144a` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'time_window', 'text': '20/1700Z - 21/0359Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 20/1700Z - 21/0359Z |
| `cand-4f776ce78dcd2597` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LGA | `fact-c9bb2fa355b03464` | `fact-c9bb2fa355b03464` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: LGA |
| `cand-5e3de266ac4eeb23` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-21T04:59:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-038:fact-06-8762570a0a5c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/21... |
| `cand-73bfdf180d1d7434` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'airport_list', 'text': 'CYHZ CYOW CYUL CYYZ CYTZ CYQB'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-7f9b32b34135a69f` | `S2_llm_schema_slice` | `initiativeComments` | ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-038:fact-07-259ab909dbe4` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/21... |
| `cand-88ad5183c21e9e6f` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `S2_llm_schema_slice:ATCSCC-GOLD-038:fact-03-4f8b4a93964a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/21... |
| `cand-8b2a266434ef0fc7` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | LGA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | CTL ELEMENT: LGA ELEMENT TYPE: APT |
| `cand-8f21f844454619c3` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'effective_time_range', 'text': '201857-210459'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201857-210459 |
| `cand-93ed92f6ae20e9b7` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'center', 'text': 'ZNY'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZNY |
| `cand-9dd1708be2f83131` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-86487ebda6091ecb` | `fact-86487ebda6091ecb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a030b7cd054fa548` | `S3_llm_schema_slice_validator_repair` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b3b7ec457847e36c` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T18:57:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-038:fact-05-d93abec3bbca` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/21... |
| `cand-b608bd2acd748b65` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T18:59:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-038:fact-04-e2d3384053d4` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/21... |
| `cand-b8fa90565d768e1d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-21T04:59:00Z | `fact-d54a9932b1320d1e` | `fact-d54a9932b1320d1e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201857-210459 |
| `cand-ba173bebea76d411` | `S2_llm_schema_slice` | `controlledNASelement` | LGA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-038:fact-02-934b8e45f41b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: LGA ELEMENT TYPE: APT ADL TIME: 1852Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 20/21... |
| `cand-d0fa4836bf3de8a9` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'weather_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d736d29deb4e3aad` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'time_window', 'text': '20/2100Z - 21/0359Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 20/2100Z - 21/0359Z |
| `cand-dda8db8ffd009884` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'flight_scope', 'text': 'ALL CONTIGUOUS US DEP DEP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-e04e0b773a133b34` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'delay_minutes', 'text': '97'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 97 |
| `cand-e6328880c270f89f` | `S1_llm_only` | `unmapped_payload` | {'class_label': 'delay_minutes', 'text': '272'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 272 |
| `cand-ec55c83854e4d643` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. | `fact-4bd7aa2a51ec9f20` | `fact-4bd7aa2a51ec9f20` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: ARR: 31 DEP: 31 TIME PLUS 30. MED HIST POP UP. GDP REVISION DUE TO THUNDERSTMORMS AND ROUTE IMPACTS. |
| `cand-ed7890f810f14261` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 115 | `fact-454b993930e032fc` | `S1b_llm_canonicalized:2026-05-20:115:fact-4a4d156590c7, fact-454b993930e032fc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM |
| `cand-f14fa0474f1f1232` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T18:59:00Z | `fact-db7ea408e290fa36` | `fact-db7ea408e290fa36` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 18:59 |

## ATCSCC-GOLD-084 / 2026-05-17:017

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=63, est=19 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 31
- Cross-system clusters: 31
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI MESSAGE: EVENT TIME: 17/1900 - 18/0200 CONSTRAINED FACILITIES: ZNY THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT, CUSTOMERS ARE ENCOURAGED TO FILE PUBLISHED CDR'S AND NRP PROCEDURES AROUND KNOWN FORECASTED WEATHER. THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. SWAP STATEMENT: **MORNING FORECAST** SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b6143e9eb34b5d6` | `S2_llm_schema_slice` | `reRouteType` | MISCELLANEOUS | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-0efa2ccd4ccebd00` | `S1_llm_only` | `states_planning_purpose_only` | True | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-137fdebd730d2038` | `S1_llm_only` | `recommends_published_CDR_and_NRP_use_when_no_route_advisories` | file published CDR's and NRP procedures around known forecasted weather | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IF NO ATCSCC ROUTE ADVISORIES ARE IN EFFECT, CUSTOMERS ARE ENCOURAGED TO FILE PUBLISHED CDR'S AND NRP PROCEDURES AROUND KNOWN FORECASTED WEATHER. |
| `cand-2a2d8867cd93dd12` | `S1_llm_only` | `may_have_additional_reroutes_for_effected_airways_outside_ZNY` | True | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDITIONAL DEPARTURE REROUTES MAY BE POSSIBLE FOR IMPACTS TO EFFECTED AIRWAYS OUTSIDE ZNY. |
| `cand-32a80b991ec164db` | `S1_llm_only` | `names_destinations_to_file_normal_routes` | ATL/CLT/MDW/ORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. |
| `cand-41e3047895aa39b8` | `S1_llm_only` | `possible_active_time` | AFT ( XXX )Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY HOTLINE POSSIBLE AFT ( XXX )Z: 540-359-3200 PIN #2778 |
| `cand-4692e1d165f39990` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 17 | `fact-65c96d5d5d95a928` | `fact-65c96d5d5d95a928` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-48356baef1c9b000` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T11:40:00Z | `fact-779511c2d280bf44` | `fact-779511c2d280bf44` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171140-180230 |
| `cand-4dd9b84bfb0b9c7c` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-5305cbb7917807c2` | `S1_llm_only` | `expects_impact_area` | ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. |
| `cand-6395dcbaf59fe613` | `S2_llm_schema_slice` | `implementationStatus` | FYI | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `cand-67ea915c6eed7c08` | `S1_llm_only` | `identifies_weather_avoidance_plans_as_possible` | True | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) |
| `cand-68e83ff1a7ad4644` | `S2_llm_schema_slice` | `initiativeComments` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | THIS ADVISORY IS FOR PLANNING PURPOSES ONLY. |
| `cand-6b9ad235923f168a` | `S1_llm_only` | `will_provide_reroutes_or_CDRs_as_necessary` | True | `` | `` | `{"rejected_schema": 3}` | `{"unknown_object_class": 3, "unknown_predicate": 3, "unknown_subject_class": 3}` | POSSIBLE REROUTES / CDR'S WILL BE PROVIDED AS NECESSARY. |
| `cand-6dbe83ed14420c4c` | `S2_llm_schema_slice` | `initiativeComments` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EXPECTED IMPACT AREA( S ): ISO-SCT TS MOVG E OVR NRN ZDC/FAR SRN ZNY. |
| `cand-74f4b3cf95df1872` | `S1_llm_only` | `encourages_compliance_with` | all ATCSCC route advisories | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO COMPLY WITH ALL ATCSCC ROUTE ADVISORIES. |
| `cand-77c3e973c5e43eae` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-7c9c88f92df2a1ae` | `S1_llm_only` | `impact_status` | not_expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DITCH IMPACTS ARE: NOT EXPECTED |
| `cand-8a871f260b7c132b` | `S1_llm_only` | `states_impacts_to_j6_q75_and_dc_metros` | possible | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTS TO J6-Q75 & DC METROS PSBL. |
| `cand-9060b0a603cfa082` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | THE FOLLOWING DESTINATIONS: ATL/CLT/MDW/ORD SHOULD FILE NORMAL ROUTES. ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. |
| `cand-9fef01d12ee6215d` | `S1_llm_only` | `identifies_constrained_facility` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-ab3ef1e8545a2aa6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T02:30:00Z | `fact-d3235e4358f93a27` | `fact-d3235e4358f93a27` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171140-180230 |
| `cand-b16fb95f8f8202ba` | `S1_llm_only` | `describes_swap_as_possible` | True | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SWAP IS POSSIBLE |
| `cand-c4682ce485b65159` | `S1_llm_only` | `impact_status` | not_expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AZEZU-PAEPR-HANRI ( L453-Y493 ) IMPACTS ARE: NOT EXPECTED |
| `cand-c8e2840256a89dbb` | `S1_llm_only` | `impact_status` | not_expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INTERNATIONAL DEPARTURES ( EAST GATES ) IMPACTS ARE: NOT EXPECTED |
| `cand-cbf228d4e71f2f8c` | `S1_llm_only` | `effective_time` | 171140-180230 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171140-180230 |
| `cand-e387a6420f36dea8` | `S1_llm_only` | `will_provide_alternate_routes_to_destinations` | ATL/CLT/MDW/ORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY/ATCSCC WILL PROVIDE ALTERNATE ROUTES TO THESE DESTINATIONS AS NEEDED. |
| `cand-e83bf11585c5604a` | `S2_llm_schema_slice` | `initiativeComments` | SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SWAP STATEMENT: **MORNING FORECAST** SWAP IS POSSIBLE SEVERE WEATHER AVOIDANCE PLANS ARE ( POSSIBLE ) FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). |
| `cand-f2026a1c01b83167` | `S1_llm_only` | `specifies_area_and_time` | ZNY area today/ after ( 19Z ) | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FOR THE ZNY AREA TODAY/ AFTER ( 19Z ). |
| `cand-f2602070fad5a455` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `implementationStatus` | FYI | `fact-8960d96363ea5bf5` | `fact-8960d96363ea5bf5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _FYI |
| `cand-f4acd7d8dd0dfc99` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T11:40:00Z | `fact-5fed3c070708740f` | `fact-5fed3c070708740f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 11:40 |

## ATCSCC-GOLD-100 / 2026-05-17:071

- Batch: `batch_10`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_10.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=61, est=18 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 30
- Cross-system clusters: 30
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=71

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 172057 WSI DDS:172058 VA ADVISORY DTG: 20260517/2057Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0005 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/488 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: OCNL VA EMS EST VA DTG: 17/2030Z EST VA CLD: SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747 MOV NW 5KT FCST VA CLD +6HR: 18/0230Z SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748 FCST VA CLD +12HR: 18/0830Z NO VA EXP FCST VA CLD +18HR: 18/1430Z NO VA EXP RMK: VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. VA EMS MAY CON...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0043172ece849d92` | `S1_llm_only` | `'expected_movement'}` | {'class': 'movement_expectation', 'text': 'WNW MVMT EXP THRU T+6'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. WNW MVMT EXP THRU T+6. |
| `cand-04e080f334f86f9b` | `S1_llm_only` | `'forecast_expectation'}` | {'class': 'forecast_status', 'text': 'NO VA EXP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 18/1430Z NO VA EXP |
| `cand-0788bdad7b921deb` | `S1_llm_only` | `'located_in_area'}` | {'class': 'area', 'text': 'ECUADOR'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-1f90573ef4dae869` | `S1_llm_only` | `'estimated_ash_datetime'}` | {'class': 'datetime_utc', 'text': '17/2030Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 17/2030Z |
| `cand-2e5d6fe7ff72c3d1` | `S1_llm_only` | `'not_visible_reason'}` | {'class': 'weather_condition', 'text': 'MET CLD CVR'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. |
| `cand-30c9bfdeb69a409c` | `S1_llm_only` | `'based_on'}` | {'class': 'forecast_basis', 'text': 'MDL GUIDANCE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST BASED ON MDL GUIDANCE. |
| `cand-3b30320e058a48d2` | `S1_llm_only` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/0230Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 18/0230Z |
| `cand-3cd8a846fd12c7aa` | `S1_llm_only` | `'eruption_details_state'}` | {'class': 'eruption_activity', 'text': 'OCNL VA EMS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: OCNL VA EMS |
| `cand-50e92732f3853355` | `S1_llm_only` | `'has_advisory_number'}` | {'class': 'advisory_number', 'text': '2026/488'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/488 |
| `cand-58824fb5a501dfc3` | `S1_llm_only` | `'movement_direction_speed'}` | {'class': 'movement', 'text': 'NW 5KT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 5KT |
| `cand-5b869eb294288418` | `S1b_llm_canonicalized` | `impactingCondition` | met cld cvr | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | VA NOT VISIBLE IN STLT IMG DUE TO MET CLD CVR. |
| `cand-66ab6ac13ac97ee5` | `S1_llm_only` | `'forecast_extent'}` | {'class': 'airspace_extent', 'text': 'SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 18/0230Z SFC/FL150 N0000 W07748 - S0004 W07739 - S0005 W07740 - S0002 W07749 - N0000 W07748 |
| `cand-6dcf912bdeab0e74` | `S1_llm_only` | `'estimated_ash_extent'}` | {'class': 'airspace_extent', 'text': 'SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 N0001 W07747 - S0004 W07739 - S0005 W07739 - S0001 W07749 - N0001 W07747 |
| `cand-71dc1622d738d609` | `S1_llm_only` | `'is_bulletin_title'}` | {'class': 'bulletin_title', 'text': 'VOLCANIC ACTIVITY BULLETIN - REVENTADOR'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-82b1a94b2721ae83` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - REVENTADOR | `` | `S2_llm_schema_slice:ATCSCC-GOLD-100:fact-05-7ca46e506509` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-82d396049150757b` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-17T17:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-100:fact-03-dc29a6304d40` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-86b6bf8993bc4a42` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T00:00:00Z | `fact-d13ed27cf169725c` | `fact-d13ed27cf169725c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-8e211f350e2c1a6f` | `S1_llm_only` | `'has_volcano_position'}` | {'class': 'position', 'text': 'S0005 W07739'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: REVENTADOR 352010 PSN: S0005 W07739 |
| `cand-95875ff45a80e25c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T20:57:00Z | `fact-71f1e021b6cff73c` | `fact-71f1e021b6cff73c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:58 |
| `cand-aa18ccacf46e5cb8` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-17T17:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-100:fact-02-bf1c95b878f9` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-afe7396785d7f8a5` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-17T20:58:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-100:fact-04-12206f24f9af` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:58 |
| `cand-b7bc53fa0c4b32e0` | `S1_llm_only` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/0830Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 18/0830Z NO VA EXP |
| `cand-b99df757e16e0bda` | `S1b_llm_canonicalized` | `advisoryNumber` | 71 | `` | `S1b_llm_canonicalized:2026-05-17:071:fact-10c2e13cda63` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/488 |
| `cand-b9b3b70214007e05` | `S1_llm_only` | `'forecast_expectation'}` | {'class': 'forecast_status', 'text': 'NO VA EXP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 18/0830Z NO VA EXP |
| `cand-cd2a63c36777cda2` | `S1_llm_only` | `'has_advisory_datetime'}` | {'class': 'datetime_utc', 'text': '20260517/2057Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260517/2057Z |
| `cand-cf17250c9ee11442` | `S1_llm_only` | `'forecast_time'}` | {'class': 'datetime_utc', 'text': '18/1430Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 18/1430Z NO VA EXP |
| `cand-e0984ab5e2d31982` | `S1_llm_only` | `'source_elevation_is'}` | {'class': 'elevation', 'text': '11686 FT AMSL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-edc6c0a672b53c5e` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 71 | `fact-b52168d2484b4409` | `S1b_llm_canonicalized:2026-05-17:071:fact-54f048fe8e08, S2_llm_schema_slice:ATCSCC-GOLD-100:fact-01-ae712dd04517, fact-b52168d2484b4409` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-fb4c6cd04f04f2d4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `fact-9fded4f2be652d07` | `fact-9fded4f2be652d07` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-fb60087f9c791397` | `S1_llm_only` | `'may_continue'}` | {'class': 'activity_continuation', 'text': 'CONT.'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |

## ATCSCC-GOLD-050 / 2026-05-19:043

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=59, est=18 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 29
- Cross-system clusters: 29
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=43

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 191422 WSI DDS:191425 VA ADVISORY DTG: 20260519/1422Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/582 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: FRQT VA EMS OBS VA DTG: 19/1350Z OBS VA CLD: SFC/FL150 N1429 W09052 - N1427 W09053 - N1415 W09158 - N1429 W09209 - N1429 W09052 MOV SW 15KT FCST VA CLD +6HR: 19/2000Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1402 W09156 - N1416 W09208 - N1429 W09053 FCST VA CLD +12HR: 20/0200Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1404 W09158 - N1420 W09208 - N1429 W09053 FCST VA CLD +18HR: 20/0800Z SF...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04299106baecec89` | `S1_llm_only` | `has_volcano_identifier` | 342090 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 |
| `cand-1748354d26606758` | `S1_llm_only` | `estimated_extent_from_summit` | approx 70 NM WSW | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXTG APPRX 70 NM WSW FM SUMMIT |
| `cand-1e59bba76c557898` | `S1_llm_only` | `has_advisory_number` | 2026/582 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/582 |
| `cand-22ec16a2658812cb` | `S1_llm_only` | `expected_shift_by_time_horizon` | shift SW by T+18 HRS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WSW MVMT EXP TO SHIFT SW BY T+18 HRS |
| `cand-26505a51e8da3bc4` | `S1_llm_only` | `has_source_elevation` | 12346 FT AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-303a63bb0d096eb8` | `S1_llm_only` | `eruption_activity_description` | FRQT VA EMS OBS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: FRQT VA EMS OBS |
| `cand-319ef57f78332c7e` | `S1_llm_only` | `has_advisory_date_time` | 20260519/1422Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260519/1422Z |
| `cand-4dedb5c38e250e6e` | `S1_llm_only` | `observed_in` | WEBCAM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBSD IN WEBCAM |
| `cand-4eaa09c8586fc0ae` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-5c4e9ac75fba9220` | `S1b_llm_canonicalized` | `advisoryNumber` | 43 | `` | `S1b_llm_canonicalized:2026-05-19:043:fact-fc0325bb927d` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/582 |
| `cand-6aad154464b98b10` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T14:25:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:25 |
| `cand-8320c7006342b665` | `S1_llm_only` | `observed_in` | STLT IMG | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBSD IN WEBCAM AND STLT IMG |
| `cand-8384b05341be71e2` | `S1_llm_only` | `based_on` | WEBCAM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-87bb111e97f8498d` | `S2_llm_schema_slice` | `advisoryNumber` | 43 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-89bd307ae9d1d5ee` | `S1_llm_only` | `observation_time` | 19/1350Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 19/1350Z |
| `cand-92184801dc9ef3ac` | `S1_llm_only` | `has_advisory_title` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-935e2f841e7d5561` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T14:22:00Z | `fact-4b893ad96835a8d7` | `fact-4b893ad96835a8d7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 14:25 |
| `cand-93db1e68bfca7bac` | `S1_llm_only` | `based_on` | NWP MDLS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-9e7b93f320438d90` | `S1_llm_only` | `based_on` | STLT OBS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVMT AND HGT BASED ON WEBCAM, STLT OBS AND NWP MDLS |
| `cand-afaf801c0d8dc4eb` | `S1_llm_only` | `observed_movement_direction` | SW | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 15KT |
| `cand-b07a0149bc89bc49` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T19:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-b09e7ac4ca29c533` | `S1_llm_only` | `observed_flight_level_range` | SFC/FL150 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL150 |
| `cand-b1f60397af7edbf3` | `S1_llm_only` | `observed_movement_speed` | 15KT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 15KT |
| `cand-cf92eb9bbb161e1a` | `S1_llm_only` | `is_reported_by` | WASHINGTON VAAC | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: WASHINGTON |
| `cand-db6c88d073002906` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `fact-3b8e92a773cd4e11` | `fact-3b8e92a773cd4e11` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-de7615779fe65b41` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `fact-8eaa87f4c3212715` | `fact-8eaa87f4c3212715` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-e4f2d514353b927d` | `S1_llm_only` | `is_located_in_area` | GUATEMALA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: GUATEMALA |
| `cand-eb82000d3b8597b5` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-fa1b8ebb4188190d` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 43 | `fact-469356323d380955` | `S1b_llm_canonicalized:2026-05-19:043:fact-54703aa81c16, fact-469356323d380955` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |

## ATCSCC-GOLD-077 / 2026-05-19:001

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=59, est=18 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 29
- Cross-system clusters: 29
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=1

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL MESSAGE: FVXX24 KNES 190010 WSI DDS:190011 VA ADVISORY DTG: 20260519/0010Z VAAC: WASHINGTON VOLCANO: POPOCATEPETL 341090 PSN: N1901 W09837 AREA: MEXICO SOURCE ELEV: 17693 FT AMSL ADVISORY NR: 2026/195 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: OCNL VA EMS EST VA DTG: 18/2356Z EST VA CLD: SFC/FL220 N1911 W09828 - N1909 W09825 - N1901 W09837 - N1901 W09837 - N1911 W09828 MOV NE 15KT FCST VA CLD +6HR: 19/0600Z SFC/FL220 N1911 W09826 - N1908 W09824 - N1901 W09837 - N1901 W09837 - N1911 W09826 FCST VA CLD +12HR: 19/1200Z NO VA EXP FCST VA CLD +18HR: 19/1800Z NO VA EXP RMK: VA NOT DETECTED IN STLT IMG. VA EMS MAY CONT. MDL GUIDANC...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01135dad86d3898a` | `S1_llm_only` | `forecast_status_is` | {'label': 'No volcanic ash expected', 'type': 'forecast_status'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 19/1800Z NO VA EXP |
| `cand-02befe81e9fafb0d` | `S1_llm_only` | `has_advisory_date_time` | {'label': '20260519/0010Z', 'type': 'advisory_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260519/0010Z |
| `cand-097da75ed102db97` | `S1b_llm_canonicalized` | `advisoryNumber` | 1 | `` | `S1b_llm_canonicalized:2026-05-19:001:fact-f7502b674cfb` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/195 |
| `cand-141fdab2d06be4af` | `S1_llm_only` | `observation_result_is` | {'label': 'Volcanic ash not detected', 'type': 'observation_result'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: VA NOT DETECTED IN STLT IMG. |
| `cand-19042885bb391bc1` | `S1_llm_only` | `movement_speed_is` | {'label': '15KT', 'type': 'speed'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 15KT |
| `cand-1e90c46027b5bd54` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `fact-f7a02b5ba9acb313` | `fact-f7a02b5ba9acb313` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-271cb418bd5158af` | `S1_llm_only` | `has_advisory_identifier` | {'label': 'ATCSCC ADVZY 001 DCC 05/19/2026', 'type': 'advisory_identifier'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-2e50a5b90dc6c6d6` | `S1_llm_only` | `has_topic` | {'label': 'Volcanic activity bulletin for Popocatepetl', 'type': 'bulletin_topic'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-3597279457eef4b0` | `S1_llm_only` | `information_sources_include` | {'label': 'GOES-19', 'type': 'information_source'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. NWP MODELS. |
| `cand-54780f9e913c93d5` | `S2_llm_schema_slice` | `advisoryNumber` | 1 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-74d6d3822f295a74` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 1 | `fact-b54fa527bc44e98c` | `S1b_llm_canonicalized:2026-05-19:001:fact-ee85887d521f, fact-b54fa527bc44e98c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-88ca64d174f7f54f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T00:10:00Z | `fact-c53bd3aff66401f4` | `fact-c53bd3aff66401f4` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 00:11 |
| `cand-957b310ccafb7952` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `fact-0b8010e63df903b9` | `fact-0b8010e63df903b9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-96f245b3cbd0ace1` | `S1_llm_only` | `estimated_vertical_extent_is` | {'label': 'SFC/FL220', 'type': 'vertical_extent'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL220 |
| `cand-9d41cc81116cc2af` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T00:11:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 00:11 |
| `cand-a0f136b69092cfca` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL | `` | `` | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-a4f0da697fba746c` | `S1_llm_only` | `estimated_time_is` | {'label': '18/2356Z', 'type': 'time_expression'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 18/2356Z |
| `cand-ab14fe6982e53705` | `S1_llm_only` | `suggests_movement_toward` | {'label': 'NE through T+6', 'type': 'movement_prediction'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MDL GUIDANCE SUGGESTS NE MVMT THRU T+6. |
| `cand-ab576cd3d739f196` | `S1_llm_only` | `forecast_time_is` | {'label': '19/0600Z', 'type': 'time_expression'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/0600Z SFC/FL220 N1911 W09826 - N1908 W09824 - N1901 W09837 - N1901 W09837 - N1911 W09826 |
| `cand-b3a2cc4afbc20660` | `S1_llm_only` | `information_sources_include` | {'label': 'NWP models', 'type': 'information_source'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. NWP MODELS. |
| `cand-b65b22ba3aff21b1` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-c4b4967d23dbe62d` | `S1_llm_only` | `moves_toward` | {'label': 'NE', 'type': 'direction'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 15KT |
| `cand-c9e4068af9a45397` | `S1_llm_only` | `located_in_area` | {'label': 'Mexico', 'type': 'geographic_area'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: MEXICO |
| `cand-cd6e8e920a460b50` | `S1_llm_only` | `may_continue` | {'label': 'Yes', 'type': 'continuation_status'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
| `cand-ce060656f2947954` | `S1_llm_only` | `source_elevation_is` | {'label': '17693 FT AMSL', 'type': 'elevation'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 17693 FT AMSL |
| `cand-d5b00f1d03babea5` | `S1_llm_only` | `forecast_status_is` | {'label': 'No volcanic ash expected', 'type': 'forecast_status'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/1200Z NO VA EXP |
| `cand-eb771c8d76e8e440` | `S1_llm_only` | `has_advisory_number` | {'label': '2026/195', 'type': 'advisory_number'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/195 |
| `cand-ed056718a192127e` | `S1_llm_only` | `eruption_details_state` | {'label': 'Occasional volcanic ash emissions', 'type': 'eruption_detail'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: OCNL VA EMS |
| `cand-f95801b4d5ee96df` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |

## ATCSCC-GOLD-045 / 2026-05-20:150

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=57, est=17 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 28
- Cross-system clusters: 28
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=150

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI MESSAGE: EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISHAP, DEBRIS RESPONSE AREA(S) (DRAS) WILL BE ACTIVATED BY ATC, RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. AFFECTED AREAS EXTEND FROM STARBASE, TEXAS THROUGH PIARCO FIR FROM 2230Z TO 0043Z. IN THE EVENT OF A DRA ACTIVATION AN ADVISORY WILL BE SENT OUT WITH THE RELEVANT ACTIVATED DRA, TIME OF THE ACTIVATION, AND THE EXPECTED END TIME OF DEBRIS FALL. DEBRIS FALL COULD OCCURR FOR U...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02e3ceacfb876d0f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZHU |
| `cand-19df9507d4045023` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T21:21:00Z | `fact-de765af190d2e7ec` | `fact-de765af190d2e7ec` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:21 |
| `cand-1d5a2d0def1a992c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-21T23:00:00Z | `fact-336735474d7cbcbc` | `fact-336735474d7cbcbc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202121-212300 |
| `cand-2115441a6c3baad0` | `S1_llm_only` | `'has_affected_areas_extend_through'}` | {'label': 'Piarco FIR', 'type': 'airspace_region'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AFFECTED AREAS EXTEND FROM STARBASE, TEXAS THROUGH PIARCO FIR FROM 2230Z TO 0043Z. |
| `cand-25a51ef5f5aaab5a` | `S1_llm_only` | `'could_occur_for_up_to'}` | {'label': '151 minutes', 'type': 'duration'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEBRIS FALL COULD OCCURR FOR UP TO 151 MINUTES. |
| `cand-295ab5086f96772b` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-20T22:30:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-33cfb0cd27e41765` | `S1_llm_only` | `'announces_tentative_launch'}` | {'label': 'SpaceX SuperHeavy Starship Flt-12 launch from Starbase, Texas on May-21-2026', 'type': 'launch_event'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. |
| `cand-45ae3789e7f59ce6` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-21T22:30:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-497d040812270aae` | `S2_llm_schema_slice` | `advisoryNumber` | 150 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-4cff1b1dd7b8e68c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `implementationStatus` | FYI | `fact-d4c33b39a81c75a2` | `fact-d4c33b39a81c75a2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _FYI |
| `cand-58c59c0307045382` | `S1_llm_only` | `'instructs_flight_crews_to_be_aware_of'}` | {'label': 'possible impacts', 'type': 'operational_risk'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE FLIGHT CREWS ARE AWARE OF POSSIBLE IMPACTS |
| `cand-604258463f1eb0c3` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-21T22:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-636104dd690cea73` | `S1_llm_only` | `'names_constrained_facility'}` | {'label': 'ZHU', 'type': 'air_traffic_control_facility'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZHU |
| `cand-679173f8a21023d8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 150 | `fact-ee99468c4964bef8` | `fact-ee99468c4964bef8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-68071f9cb7cd520f` | `S1_llm_only` | `'has_event_time_window'}` | {'label': '20/2230 - 21/2230', 'type': 'time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-7657e5fc7a3e96a5` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-20T21:21:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-7f458e4c84e2e3a2` | `S1_llm_only` | `'states_update_will_announce'}` | {'label': 'involved airspace released and normal traffic resumed', 'type': 'airspace_status_update'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AN UPDATE WILL BE SENT OUT ADVISING THE INVLOVED AIRSPACE IS RELEASED AND THAT NORMAL TRAFFIC HAS RESUMED. |
| `cand-90ffe61805bda1e8` | `S1_llm_only` | `'may_trigger'}` | {'label': 'airborne holding', 'type': 'traffic_management_initiative'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-9fc5e114379bf7e3` | `S1_llm_only` | `'may_trigger'}` | {'label': 'groundstops', 'type': 'traffic_management_initiative'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-abe7a739057f2d0b` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T22:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/2230 - 21/2230 |
| `cand-aef8512994086b0f` | `S2_llm_schema_slice` | `initiativeComments` | SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXAS ON MAY-21-2026. IN THE EVENT OF A MISHAP, DEBRI... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULED TO LAUNCH FROM STARBASE, TEXA... |
| `cand-d4801c84bfd41942` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 150 | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-d4b39d5aa20c6636` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T21:21:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 21:21 |
| `cand-d5d3a9629f93f62b` | `S1_llm_only` | `'may_trigger'}` | {'label': 'route closures', 'type': 'traffic_management_initiative'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESULTING IN POSSIBLE INITIATIVES SUCH AS AIRBORNE HOLDING, ROUTE CLOSURES, AND GROUNDSTOPS. |
| `cand-da0f6018bbb1fc3f` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | EVENT TIME: 20/2230 - 21/2230 CONSTRAINED FACILITIES: ZHU PRE-MISSION ADVISORY: SPACEX SUPERHEAVY STARSHIP FLT-12 IS TENTATIVELY SCHEDULE... | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-ecdcabf170a80ac0` | `S1_llm_only` | `'instructs_flights_to_be_fueled_accordingly'}` | {'label': 'possible impacts', 'type': 'operational_risk'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AND THAT FLIGHTS ARE FUELED ACCORDINGLY. |
| `cand-f9df334fc8565a3c` | `S2_llm_schema_slice` | `controlledNASelement` | ZHU | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `cand-fb0a46fa1ae3672d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T21:21:00Z | `fact-cd6875ba2747520f` | `fact-cd6875ba2747520f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202121-212300 |

## ATCSCC-GOLD-061 / 2026-05-15:017

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=57, est=17 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 28
- Cross-system clusters: 28
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=17

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA MESSAGE: FVXX22 KNES 150845 WSI DDS:150847 VA ADVISORY DTG: 20260515/0845Z VAAC: WASHINGTON VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS SOURCE ELEV: 4009 FT AMSL ADVISORY NR: 2026/025 INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. NWP MODELS. ERUPTION DETAILS: ERUPTION CONTINUES OBS VA DTG: 15/0826Z OBS VA CLD: SFC/FL100 N1931 W15526 - N1926 W15517 - N1924 W15516 - N1921 W15532 - N1931 W15526 MOV W 10KT SFC/FL200 N2013 W15354 - N2002 W15347 - N1940 W15435 - N1946 W15444 - N2013 W15354 MOV NE 20KT FCST VA CLD +6HR: 15/1430Z SFC/FL100 N1943 W15534 - N1926 W15516 - N1924 W15516 - N1907 W15543 - N1943 W15534 SFC/FL200 NO VA...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0d1f43c517bbdeb8` | `S2_llm_schema_slice` | `controlledNASelement` | Kilauea | `` | `S2_llm_schema_slice:ATCSCC-GOLD-061:fact-06-de382f3154dc` | `{"repaired_accepted": 1}` | `{}` | VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS |
| `cand-108494ba1264d2ba` | `S1_llm_only` | `expected ash presence` | no volcanic ash expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 15/2030Z NO VA EXP |
| `cand-1b660b1cb4b21cc6` | `S1_llm_only` | `were dispersing` | toward the southwest farther from summit | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISPERSING TWD THE SW FURTHER FM SUMMIT |
| `cand-28d93016bdc95012` | `S1_llm_only` | `is in area` | Hawaiian Islands | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: HAWAIIAN.IS |
| `cand-45e6319715ece211` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-15T08:47:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-061:fact-02-eb5f7062740d` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 08:47 |
| `cand-5cd72854c0adaad1` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 17 | `fact-75f8aee4ce0ffa18` | `S2_llm_schema_slice:ATCSCC-GOLD-061:fact-01-5d693db5ddb2, fact-75f8aee4ce0ffa18` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-5f3f7dbc94ed165a` | `S1_llm_only` | `observed vertical extent` | surface to FL200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SFC/FL200 |
| `cand-606de756ffa7549f` | `S1_llm_only` | `was moving` | northeast at 20 kt | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NE 20KT |
| `cand-63cf3d9fa3945c31` | `S1_llm_only` | `is continuing` | continuing | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ERUPTION CONTINUES |
| `cand-63f3b5972ae4c7fe` | `S1_llm_only` | `expected no ash above` | FL200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SFC/FL200 NO VA EXP |
| `cand-76c1077634ae0345` | `S1_llm_only` | `is expected to dissipate by` | T+6 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXP TO DISSIPATE BY T+6 |
| `cand-7d60da4312e3a53f` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-15T15:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-061:fact-04-dfb40d6fdc42` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a08c815e7597543f` | `S1_llm_only` | `may be obscured by` | weather clouds | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FURTHER EMS MAY BE OBSC BY WX CLDS |
| `cand-a2c7d5537a96572a` | `S1_llm_only` | `were observed on satellite` | observed on satellite | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS OBS ON STLT |
| `cand-a30c76196fcd7425` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T08:45:00Z | `fact-a7f8ea60b1d07122` | `fact-a7f8ea60b1d07122` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 08:47 |
| `cand-aa3fbacf0ce685b1` | `S1_llm_only` | `has elevation` | 4009 ft AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 4009 FT AMSL |
| `cand-b9a2bea3c521b20f` | `S1_llm_only` | `expected vertical extent` | surface to FL100 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/1430Z SFC/FL100 |
| `cand-bb259b85a74406bf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `fact-f3694b05c8801d4c` | `fact-f3694b05c8801d4c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-bc3693a3ee90a31d` | `S1_llm_only` | `is expected` | northwest movement | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NW MVMT EXP AT FL100 BY T+6 |
| `cand-c99910367d0661bc` | `S1_llm_only` | `was observed` | off coast northeast from summit | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMNANT LGT VA CLD AT FL200 OBS OFF COAST NE FM SUMMIT |
| `cand-d28be65783d51422` | `S1_llm_only` | `were moving` | west-northwest from summit | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MVG WNW FM SUMMIT |
| `cand-e30fd2136754974a` | `S1_llm_only` | `expected ash presence` | no volcanic ash expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/0230Z NO VA EXP |
| `cand-e44b1b51712a5062` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `fact-5e7dace90dc36461` | `S2_llm_schema_slice:ATCSCC-GOLD-061:fact-03-45130ec50117, fact-5e7dace90dc36461` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-e4f38bb6ac9016b3` | `S1_llm_only` | `was moving` | west at 10 kt | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV W 10KT |
| `cand-e7471e3782495cb0` | `S1_llm_only` | `observed vertical extent` | surface to FL100 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL100 |
| `cand-e8a26a4e4b2ca787` | `S1_llm_only` | `is possible` | southwest dispersion | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WITH DISPERSION SW PSBL |
| `cand-e8e6c4f1bb3be722` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - KILAUEA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-061:fact-05-cd646f584495` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-fdd8f03df3fd3f0b` | `S1_llm_only` | `is the volcano named in the advisory` | Kilauea | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: KILAUEA |

## ATCSCC-GOLD-072 / 2026-05-17:065

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=57, est=16 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 28
- Cross-system clusters: 28
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=65

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 172012-180330 SIGNATURE: 26/05/17 20:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0836bb48ae941599` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-17T17:20:12Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-02-45f56a27fa6a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CD... |
| `cand-0bb0125a03fbbbcc` | `S1_llm_only` | `'revision_relation'}` | {'label': 'Advisory 016', 'type': 'advisory_notice'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES / EXTENDS ADVZY 016*** |
| `cand-0d21c78cfc18986c` | `S3_llm_schema_slice_validator_repair` | `reRouteType` | CDR | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-15ad88bebac63e88` | `S1_llm_only` | `'time_window_relation'}` | {'label': '17/1130 - 18/0300', 'type': 'time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 17/1130 - 18/0300 |
| `cand-23b50ba4dc81e752` | `S1_llm_only` | `'relation'}` | {'label': 'weather', 'type': 'weather_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-24a3bf6042403447` | `S1_llm_only` | `'instruction'}` | {'label': 'users', 'type': 'airspace_users'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-27ac2635c157e0bb` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | REPLACES / EXTENDS ADVZY 016; USERS SHOULD FUEL ACCORDINGLY. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-42e85615939cfaeb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 65 | `fact-4b1a4174e270c7aa` | `fact-4b1a4174e270c7aa` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-5077c739350a3080` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-18T03:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 172012-180330 |
| `cand-6e056cf7a018cbb0` | `S2_llm_schema_slice` | `controlledNASelement` | ORD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-09-8c694b72b0c3` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-796e5b613393a7c3` | `S3_llm_schema_slice_validator_repair` | `implementationStatus` | FYI | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-7f9f6f2e67b5491d` | `S2_llm_schema_slice` | `initiativeComments` | EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. USE... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-07-e05f4374ac1f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CD... |
| `cand-879f4f1180835934` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T03:03:30Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-03-057170929349` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CD... |
| `cand-8ad7891c76a43826` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T03:30:00Z | `fact-07590123e8ca37d5` | `fact-07590123e8ca37d5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-8d2e5d2e319a1e2c` | `S2_llm_schema_slice` | `implementationStatus` | FYI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-04-367ced6578bf` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CD... |
| `cand-8f27da119c90b034` | `S2_llm_schema_slice` | `advisoryNumber` | 65 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-01-bc430cc4feb7` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CD... |
| `cand-92c263e59792f059` | `S1_llm_only` | `'relation'}` | {'label': 'ZAU', 'type': 'air_traffic_facility'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-a3525d075d9183c3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T20:12:00Z | `fact-7b7d434662f299b0` | `fact-7b7d434662f299b0` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 20:12 |
| `cand-a41dd49d06c4aafa` | `S1b_llm_canonicalized` | `advisoryNumber` | 65 | `` | `S1b_llm_canonicalized:2026-05-17:065:fact-43e765eb448e` | `{"repaired_accepted": 1}` | `{}` | ***REPLACES / EXTENDS ADVZY 016*** |
| `cand-ac83650d3c94de8a` | `S2_llm_schema_slice` | `controlledNASelement` | ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-ad091a658aedd71b` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-06-0dccdcd9c75c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CD... |
| `cand-ae3173c6a8d3ddc2` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-17T20:12:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 172012-180330 |
| `cand-bc30d4766467fbd3` | `S3_llm_schema_slice_validator_repair` | `reRouteReason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ZAU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-c4979921fb96e833` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-d86cd55b89470f37` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'label': 'ZAU', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU |
| `cand-e2a42f88570cefc6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T20:12:00Z | `fact-251e2d256e27a244` | `fact-251e2d256e27a244` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 172012-180330 |
| `cand-e71777b347fe543f` | `S2_llm_schema_slice` | `controlledNASelement` | MDW | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-10-dfb207818f8d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `cand-fc6b0f29afb0d6cc` | `S2_llm_schema_slice` | `reRouteType` | CDR | `` | `S2_llm_schema_slice:ATCSCC-GOLD-072:fact-05-7b49b7be1069` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI MESSAGE: EVENT TIME: 17/1130 - 18/0300 CONSTRAINED FACILITIES: ZAU ***REPLACES / EXTENDS ADVZY 016*** ZAU IS IMPLEMENTING CD... |

## ATCSCC-GOLD-041 / 2026-05-18:054

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=55, est=16 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 27
- Cross-system clusters: 27
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=54

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. EFFECTIVE TIME: 181357-181630 SIGNATURE: 26/05/18 13:57 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0287280efd166879` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | SIGNATURE: 26/05/18 13:57 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 13:57 |
| `cand-0d7f20c246594bb1` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-1045c190186daf1d` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-17318a6a0c6a8ef0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T13:57:00Z | `fact-999fefd57f1e4856` | `fact-999fefd57f1e4856` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181357-181630 |
| `cand-1da2aa2b2d1a7caa` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-2002b3c636436b34` | `S1_llm_only` | `'should_file'}` | {'label': 'alternate routing', 'type': 'routing_action'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-2cfeb9fe98b30060` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 54 | `fact-d6caf0924fa393aa` | `fact-d6caf0924fa393aa` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-32d57d45dd7a83ca` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T13:57:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-36132ba27682f08d` | `S1_llm_only` | `'removes'}` | {'label': 'L455', 'type': 'route'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *REMOVES L455* |
| `cand-456f37f194722a42` | `S1_llm_only` | `'is_closed_due_to'}` | {'label': 'thunderstorms', 'type': 'weather_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-4cf1162854bcfe9c` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T16:30:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-5c45f237fb294308` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T16:30:00Z | `fact-1c59c351822c0d5e` | `fact-1c59c351822c0d5e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181357-181630 |
| `cand-5caeab04cd6aef4c` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-92274698b0dbed3c` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T13:57:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-9229b9ee1c03099a` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | CONSTRAINED FACILITIES: ZNY | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-9b2ca28d9b1e64a3` | `S1_llm_only` | `'replaces'}` | {'label': 'advisory 035', 'type': 'advisory'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES ADVZY 035*** |
| `cand-a7ae44b32c339560` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-a8ca574b029dd68f` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | EVENT TIME: 18/1130 - 18/1600 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1130 - 18/1600 |
| `cand-b0d0a176accf52ca` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `fact-5f2725815065cad1` | `fact-5f2725815065cad1` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-b5f37bebb9882144` | `S2_llm_schema_slice` | `initiativeComments` | OCEANIC ROUTE CLOSURE_RQD | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-bdc0022818fce3cb` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | USERS SHOULD FILE ALTERNATE ROUTING. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-ce83d0fb832a910c` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-d1545d44d0f09055` | `S1b_llm_canonicalized` | `advisoryNumber` | 54 | `` | `S1b_llm_canonicalized:2026-05-18:054:fact-10d3088cc8a9` | `{"repaired_accepted": 1}` | `{}` | ***REPLACES ADVZY 035*** |
| `cand-e01da3ff59c89ba3` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1130 - 18/1600 CONSTRAINED FACILITIES: ZNY ***REPLACES ADVZY 035*** *REMOVES L455* ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNA... |
| `cand-e45ab184a633715f` | `S1_llm_only` | `'constrains_facility'}` | {'label': 'ZNY', 'type': 'facility'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-f43b03e61ed3f6cc` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T13:57:00Z | `fact-d5bc5b6b960557bd` | `fact-d5bc5b6b960557bd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 13:57 |
| `cand-feed894093738348` | `S2_llm_schema_slice` | `advisoryNumber` | 54 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD ... ZNY ADVISES THAT L453 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. |

## ATCSCC-GOLD-067 / 2026-05-15:030

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=55, est=17 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 27
- Cross-system clusters: 27
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=30

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA MESSAGE: FVXX22 KNES 151223 WSI DDS:151225 VA ADVISORY DTG: 20260515/1223Z VAAC: WASHINGTON VOLCANO: KILAUEA 332010 PSN: N1925 W15517 AREA: HAWAIIAN.IS SOURCE ELEV: 4009 FT AMSL ADVISORY NR: 2026/026 INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. SOCIAL MEDIA. ERUPTION DETAILS: VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO VA EXP FCST VA CLD +18HR: 16/0600Z NO VA EXP RMK: RECENT VOL EPISODE CEASED AND VA DISPERSED. RESIDUAL VA MAY LINGER IN THE LOW LEVELS NEAR THE SUMMIT. SO2, WATER VAPOR AND OTHER GASES MAY EXTEND FURTHER. ...L...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04f373de3af1ffe0` | `S1_llm_only` | `has_consequence` | volcanic ash dispersed | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RECENT VOL EPISODE CEASED AND VA DISPERSED. |
| `cand-0c6ea835bf22e2a3` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-15a28fa17cb35343` | `S1_llm_only` | `has_source_elevation` | 4009 ft AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 4009 FT AMSL |
| `cand-1834d603bd7c80cf` | `S1_llm_only` | `is_located_in_area` | Hawaiian Islands | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: HAWAIIAN.IS |
| `cand-1d103e7cedf3c2f7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T12:23:00Z | `fact-853ac37fd042d171` | `fact-853ac37fd042d171` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 12:25 |
| `cand-2243b4c7123eb473` | `S1_llm_only` | `has_forecast_at_plus_6_hours` | no volcanic ash expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 15/1800Z NO VA EXP |
| `cand-263030572632cccd` | `S1_llm_only` | `may_linger_in` | the low levels near the summit | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RESIDUAL VA MAY LINGER IN THE LOW LEVELS NEAR THE SUMMIT. |
| `cand-289261c9557b3975` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 30 | `fact-88dde419c1599eee` | `S1b_llm_canonicalized:2026-05-15:030:fact-318186f9544b, fact-88dde419c1599eee` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-367da914404ab3ec` | `S1_llm_only` | `has_forecast_at_plus_18_hours` | no volcanic ash expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/0600Z NO VA EXP |
| `cand-3fa856eed3ffa673` | `S1_llm_only` | `has_advisory_number` | 2026/026 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/026 |
| `cand-51a34614b0ad548f` | `S1_llm_only` | `was_observed_at_time` | 2026-05-15T12:01Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 15/1201Z |
| `cand-51a5b176a0e34715` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - KILAUEA | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-711767d27c32879b` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-15T12:25:00Z | `` | `` | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | SIGNATURE: 26/05/15 12:25 |
| `cand-79f73afc1c2ff0e5` | `S1_llm_only` | `was_not_identifiable_from` | satellite data | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. |
| `cand-8916645326bf8584` | `S2_llm_schema_slice` | `advisoryNumber` | 30 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `cand-915cec3637e890e4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `fact-7221a869538b242e` | `fact-7221a869538b242e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-99b622462985ab3e` | `S1_llm_only` | `may_extend_further_than` | residual volcanic ash | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SO2, WATER VAPOR AND OTHER GASES MAY EXTEND FURTHER. |
| `cand-a0748da08751ab43` | `S1_llm_only` | `effective_time_window` | 150000-150000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a3771a1351d62d35` | `S1_llm_only` | `has_forecast_at_plus_12_hours` | no volcanic ash expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/0000Z NO VA EXP |
| `cand-a479102971cf6bca` | `S1_llm_only` | `uses_information_sources` | GOES-18, HVO, Honolulu MWO, webcam, social media | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-18. HVO. HONOLULU MWO. WEBCAM. SOCIAL MEDIA. |
| `cand-b073c0b5630e82ee` | `S1_llm_only` | `has_eruption_status` | ended | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EMS ENDED. |
| `cand-b4a73320a1583393` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `fact-6de5445c423395eb` | `fact-6de5445c423395eb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-b846b080926d07b0` | `S1_llm_only` | `has_volcano_identifier` | 332010 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: KILAUEA 332010 |
| `cand-bb8c17c34ef25e7c` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-15T15:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 150000-150000 |
| `cand-c12236cf2e5465f3` | `S2_llm_schema_slice` | `initiativeComments` | VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EMS ENDED. OBS VA DTG: 15/1201Z OBS VA CLD: VA NOT IDENTIFIABLE FROM SATELLITE DATA. FCST VA CLD +6HR: 15/1800Z NO VA EXP FCST VA CLD +12HR: 16/0000Z NO VA... |
| `cand-edaf08f398406d89` | `S1b_llm_canonicalized` | `advisoryNumber` | 30 | `` | `S1b_llm_canonicalized:2026-05-15:030:fact-c106e41a607f` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/026 |
| `cand-f2f0bc571c94761b` | `S1_llm_only` | `identifies_current_hazard_as` | volcanic activity bulletin for Kilauea | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |

## ATCSCC-GOLD-068 / 2026-05-18:126

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=55, est=16 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 27
- Cross-system clusters: 27
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=126

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-07ad3c58c7e84222` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport(STL) | `` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-09-5c5ebd5ce279` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT |
| `cand-0820a5058d36a750` | `S2_llm_schema_slice` | `extensionProbability` | LOW | `` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-02-43541025c9d0` | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 18/2030Z - 19/0003Z |
| `cand-0a44c63a382383ee` | `S1_llm_only` | `has_signature_timestamp` | 26/05/18 20:33 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:33 |
| `cand-0deddcdb76a2d35e` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | NONE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-068:fact-02-ee1e83e44535` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-12f24f4ddcd84477` | `S1_llm_only` | `has_ground_stop_action` | GS CNX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-16d54005e27b215f` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T20:33:00Z | `fact-250ad95527b5dfa5` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-05-724c7031f54e, fact-250ad95527b5dfa5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/18 20:33 |
| `cand-198559a61fcc1846` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T20:33:00Z | `fact-dbee78c27010f517` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-06-f7a922a1f978, fact-dbee78c27010f517` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-1ba81f7ec784b7d2` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-18T20:33:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-068:fact-05-733bbb6d1792` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-2b25bcc1555e0368` | `S1_llm_only` | `has_activity_time` | 2030Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-2be77d9a89e040fe` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | other | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-068:fact-03-e330d3f124ef` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-40a21f39721e0673` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-18T20:33:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-068:fact-04-d4428a28103c` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:33 |
| `cand-450d3162700c797a` | `S1_llm_only` | `has_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-46e3be7f7401aa35` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-19T01:03:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-068:fact-06-e98cdbf330d7` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-4dbc8c235de2f1de` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | nas:Airport(STL) | `` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-01-8cd4fe88e893, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-068:fact-01-8cd4fe88e893` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT |
| `cand-50485eef76606d70` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 126 | `fact-65e82a0b7dc6b447` | `S1b_llm_canonicalized:2026-05-18:126:fact-1f936a7cf4f2, fact-65e82a0b7dc6b447` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX |
| `cand-59d01401c9835199` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-32956aec5a36978b` | `fact-32956aec5a36978b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182033-190103 SIGNATURE: 26/05/18 20:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-5df9d45722dc5cd5` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T01:03:00Z | `fact-050bc2cd0912713d` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-07-9d231a65a8bf, fact-050bc2cd0912713d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 182033-190103 |
| `cand-655418d6fedf5993` | `S2_llm_schema_slice` | `impactingCondition` | other | `` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-03-3cc658b79cac` | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 18/2030Z - 19/0003Z |
| `cand-7dad81f38bd8c181` | `S1_llm_only` | `names_control_element` | STL ELEMENT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-8797c5b2fab74412` | `S1_llm_only` | `has_advisory_identifier` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX |
| `cand-8b33dafb74a2ea19` | `S2_llm_schema_slice` | `extensionProbability` | LOW | `` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-08-bc7a549f0422` | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 18/2030Z - 19/0003Z |
| `cand-8cb41f8ff998733b` | `S1_llm_only` | `has_effective_time_range` | 182033-190103 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182033-190103 |
| `cand-99143c15a6c0787f` | `S2_llm_schema_slice` | `advisoryNumber` | 126 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-068:fact-04-d5aa5cbe4e0e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 |
| `cand-a0e221613c4deb9f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `fact-82cd32f6f0f75253` | `fact-82cd32f6f0f75253` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-d8ce39d5c1ccc177` | `S1_llm_only` | `has_operational_period` | 18/2030Z - 19/0003Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |
| `cand-f47f15ceeca0b97b` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | GS CNX PERIOD: 18/2030Z - 19/0003Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-068:fact-07-ec831115a5ea` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182033-190103 |
| `cand-f4d9617286cd213e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `` | `S1b_llm_canonicalized:2026-05-18:126:fact-0374dbf8862d` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2030Z GS CNX PERIOD: 18/2030Z - 19/0003Z COMMENTS: |

## ATCSCC-GOLD-093 / 2026-05-18:060

- Batch: `batch_10`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_10.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=55, est=17 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 27
- Cross-system clusters: 27
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=60

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 18/1445 - 18/1800 CONSTRAINED FACILITIES: ZKC THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. EFFECTIVE TIME: 181444-181830 SIGNATURE: 26/05/18 14:44 FAA.gov Home \| Privacy Policy \| Web Policies &...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04e26b944dffdd8a` | `S2_llm_schema_slice` | `initiativeComments` | CONSTRAINED FACILITIES: ZKC | `` | `S2_llm_schema_slice:ATCSCC-GOLD-093:fact-06-013ef7dca53a` | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZKC |
| `cand-09bb6a84bdcb8045` | `S1_llm_only` | `'will_close_at_end_of'}` | {'label': 'the event time specified in this advisory', 'type': 'time_reference'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-0e819541e6805145` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DELAY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-14efb6f96dbcc899` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 60 | `fact-cc4fdab5a2292fe2` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-093:fact-01-395951e2ec7a, fact-cc4fdab5a2292fe2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-26a1a6bb2008d57b` | `S2_llm_schema_slice` | `initiativeComments` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-093:fact-05-c5c891cbbcb4` | `{"repaired_accepted": 1}` | `{}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. |
| `cand-29f1e5db9b12aea9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T18:30:00Z | `fact-be88d25b5bb94599` | `fact-be88d25b5bb94599` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-2a08086ed539a6cd` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMAR... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-093:fact-05-8ed515f3812f` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-2ec2441fd533cf45` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-18T18:14:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-093:fact-03-7d446d6f1219` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-561356876a787410` | `S1_llm_only` | `'will_close_for'}` | {'label': 'STL Airport', 'type': 'airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-56392a5bcdbd4492` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T18:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-093:fact-04-817992e39828` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-57560f139586511a` | `S1_llm_only` | `'are_not_automatically_exempt_when_ground_delay_program_or_ground_stop_exists...` | {'label': 'Ground Delay Program or Ground Stop at destination airport', 'type': 'traffic_management_program_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-626fcba3510612de` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T14:44:00Z | `fact-0b35dc5e9170823f` | `fact-0b35dc5e9170823f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-67371d27a1eed012` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T14:44:00Z | `fact-8a40c9b0d75d6128` | `fact-8a40c9b0d75d6128` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:44 |
| `cand-6a8751830cc894c8` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T14:44:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-093:fact-02-a57a8a2ed8b4` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:44 |
| `cand-6bf115c388c9c967` | `S1_llm_only` | `'identifies_constrained_facilities'}` | {'label': 'ZKC', 'type': 'facility_area'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZKC |
| `cand-713fe7ef1ca12b79` | `S2_llm_schema_slice` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-76ca50f592d94547` | `S1_llm_only` | `'should_ensure_diversion_remarks_include'}` | {'label': 'DVRSN', 'type': 'flight_plan_remark_code'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-7b675e048434f53e` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-18T14:44:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-093:fact-02-f4f42c5dd6af` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-9a9e0435d761ce78` | `S2_llm_schema_slice` | `initiativeComments` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-093:fact-07-c7b881f71517` | `{"repaired_accepted": 1}` | `{}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR STL AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-b2f246ec34137756` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-18T18:18:30 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-093:fact-04-a316680d9cd1` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-bf8c6a3a1fb37fcb` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | STL AIRPORT | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-093:fact-06-2d16ab8b04fb` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-c427512e6e92d4ef` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STOP | `` | `S1b_llm_canonicalized:2026-05-18:060:fact-40819f4954e0` | `{"repaired_accepted": 1}` | `{}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-d10ca7a50b34a2d3` | `S1_llm_only` | `'will_still_receive'}` | {'label': 'EDCT', 'type': 'controlled_departure_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-e1bfc10d864d1ec4` | `S1_llm_only` | `'states_event_time'}` | {'label': '18/1445 - 18/1800', 'type': 'time_interval'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1445 - 18/1800 |
| `cand-e39d5b87da5dcf3e` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T14:44:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-093:fact-03-84d0926ac8c1` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181444-181830 |
| `cand-e8ddef3480df7175` | `S1_llm_only` | `'activated_diversion_recovery_tool_for'}` | {'label': 'STL Airport', 'type': 'airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR STL AIRPORT. |
| `cand-fe791620f05d7cf2` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZKC |

## ATCSCC-GOLD-062 / 2026-05-20:029

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=53, est=17 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 26
- Cross-system clusters: 26
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=29

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 200210 CCA WSI DDS:200212 VA ADVISORY -CORRECTION DTG: 20260520/0210Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/585 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 20/0140Z EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 MOV SW 10KT FCST VA CLD +6HR: 20/0730Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 FCST VA CLD +18HR:...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03539ede3acddc42` | `S1_llm_only` | `'announces bulletin about'}` | {'label': 'volcanic activity bulletin for Fuego', 'text': 'VOLCANIC ACTIVITY BULLETIN - FUEGO'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-0b47b4c3f64a5cff` | `S1_llm_only` | `'is located in'}` | {'label': 'Guatemala', 'text': 'AREA: GUATEMALA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-0e9c625753fcbe4c` | `S1_llm_only` | `'forecast valid at'}` | {'label': '2026-05-20 19:30Z', 'text': '20/1930Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/1930Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09052 |
| `cand-11ee12904048f60f` | `S2_llm_schema_slice` | `advisoryNumber` | 29 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-187bdb13b579f4bd` | `S1_llm_only` | `'gives reason'}` | {'label': 'weather clouds in summit area', 'text': 'WX CLDS IN SUMMIT AREA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-34363e02975eddb6` | `S1_llm_only` | `'has source elevation'}` | {'label': '12346 ft amsl', 'text': 'SOURCE ELEV: 12346 FT AMSL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-49dbf4cffb0a7bb5` | `S1_llm_only` | `'has correction timestamp'}` | {'label': '2026-05-20 02:10Z', 'text': 'DTG: 20260520/0210Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY -CORRECTION DTG: 20260520/0210Z |
| `cand-4bde08d0c6209e5a` | `S1_llm_only` | `'predicts continued emissions'}` | {'label': 'likely continue', 'text': 'LIKELY CONTINUE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-5005068bf2259314` | `S1_llm_only` | `'has speed'}` | {'label': '10 knots', 'text': 'MOV SW 10KT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-6fc2b57d4d8e27a4` | `S1_llm_only` | `'forecasts no change in model winds'}` | {'label': 'next 18 hours', 'text': 'NXT 18 HR'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-78637095de6c89cd` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-79d10aefbd3fde91` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `fact-6d2b82906f6b299a` | `fact-6d2b82906f6b299a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-8e12432071543bd1` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-91e77062fc6ee085` | `S1_llm_only` | `'has vertical extent'}` | {'label': 'surface to flight level 140', 'text': 'SFC/FL140'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 |
| `cand-a951d3b444750dc2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T02:10:00Z | `fact-7461d6ff933b29cb` | `fact-7461d6ff933b29cb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 02:12 |
| `cand-aedf2766318f8126` | `S1_llm_only` | `'forecast valid at'}` | {'label': '2026-05-20 07:30Z', 'text': '20/0730Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/0730Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 |
| `cand-af732b6f50f875e3` | `S1b_llm_canonicalized` | `impactingCondition` | weather clouds in summit area wx clds in summit area | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-b0221292e3ffd50f` | `S1_llm_only` | `'estimated start time'}` | {'label': '2026-05-20 01:40Z', 'text': '20/0140Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS EST VA DTG: 20/0140Z |
| `cand-d92fa552f8a73a89` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 29 | `fact-ff3d1c04c10e6c69` | `S1b_llm_canonicalized:2026-05-20:029:fact-d77d0dceac79, fact-ff3d1c04c10e6c69` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-db9b70461b294595` | `S1_llm_only` | `'states eruption status'}` | {'label': 'ongoing', 'text': 'ONGOING'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING |
| `cand-e8e62d03c93c4142` | `S1_llm_only` | `'reports detection status'}` | {'label': 'not detected on satellite', 'text': 'VA NOT DETECTED ON STLT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-ee234e5421e6ffdd` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T20:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-fae275b5c2185e15` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T02:12:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 02:12 |
| `cand-fc81de610a47f111` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `fact-d477602884e8e756` | `fact-d477602884e8e756` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-fe08dda77b540b98` | `S1_llm_only` | `'forecast valid at'}` | {'label': '2026-05-20 13:30Z', 'text': '20/1330Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 |
| `cand-fe4f6b0e2ccdec45` | `S1_llm_only` | `'moves toward'}` | {'label': 'southwest', 'text': 'MOV SW 10KT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |

## ATCSCC-GOLD-086 / 2026-05-16:046

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=53, est=17 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 26
- Cross-system clusters: 26
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=46

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY MESSAGE: FVAK21 PAWU 161536 WSI DDS:161538 VA ADVISORY DTG: 20260516/1536Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5558 E16035 AREA: KAMCHATKA SOURCE ELEV: 9455 FT AMSL ADVISORY NR: 2026/001 INFO SOURCE: TOKYO VAAC. ERUPTION DETAILS: NOT PROVIDED OBS VA DTG: NOT PROVIDED OBS VA CLD: NOT PROVIDED FCST VA CLD +6HR: 16/2100Z NOT PROVIDED FCST VA CLD +12HR: 17/0300Z NOT PROVIDED FCST VA CLD +18HR: 17/0900Z NOT PROVIDED RMK: PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. ...GATLING EFFECTIVE TIME: 160000-160000 SIGNATURE: 26/05/16 15:38 FAA.gov Home \|...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-020a115c95d31ef5` | `S1_llm_only` | `names_volcano` | BEZYMIANNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: BEZYMIANNY |
| `cand-078f37d973872f0a` | `S1_llm_only` | `states_eruption_details` | NOT PROVIDED | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: NOT PROVIDED |
| `cand-0b363d1a5694336b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-16T15:36:00Z | `fact-6f7061c63c6dc623` | `fact-6f7061c63c6dc623` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 15:38 |
| `cand-0cdcf31b7acb54c8` | `S1_llm_only` | `has_position` | N5558 E16035 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5558 E16035 |
| `cand-120a1a33edd8e9ff` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-16T16:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160000-160000 |
| `cand-1dedd5ac05eb5cbd` | `S1_llm_only` | `has_subject_line` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-1e8ea5c7f33dbfb7` | `S1_llm_only` | `states_forecast_volcanic_ash_cloud_plus_12_hours` | NOT PROVIDED | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 17/0300Z NOT PROVIDED |
| `cand-1f2d5d450281345e` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 46 | `fact-c9cf3a1a86f388bf` | `S1b_llm_canonicalized:2026-05-16:046:fact-d01fceda1fcf, fact-c9cf3a1a86f388bf` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-235aaa6e475751c5` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-16T16:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160000-160000 |
| `cand-264c9f98bffef555` | `S1_llm_only` | `has_effective_time_window` | 160000-160000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160000-160000 |
| `cand-3df3714097b3d05e` | `S1_llm_only` | `includes_remarks` | PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PLEASE SEE FVFE01 RJTD 161200 ISSUED BY THE TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. |
| `cand-796af776698e8cd3` | `S1_llm_only` | `has_information_source` | TOKYO VAAC | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: TOKYO VAAC. |
| `cand-7d4176d90c5e29fc` | `S1_llm_only` | `reports_issued_datetime` | 20260516/1536Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA ADVISORY DTG: 20260516/1536Z |
| `cand-867d45fb43613d03` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-16T00:00:00Z | `fact-647988b904d5bbcc` | `fact-647988b904d5bbcc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-86bf9e76b6b18d90` | `S2_llm_schema_slice` | `advisoryNumber` | 46 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 046 |
| `cand-8fb83001bff4211a` | `S1b_llm_canonicalized` | `advisoryNumber` | 46 | `` | `S1b_llm_canonicalized:2026-05-16:046:fact-a01dc62ec19a` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/001 |
| `cand-9a03559eed29a0a2` | `S1_llm_only` | `states_forecast_volcanic_ash_cloud_plus_18_hours` | NOT PROVIDED | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 17/0900Z NOT PROVIDED |
| `cand-b34f9a72478d0edd` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-16T15:38:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 15:38 |
| `cand-bb064abb171c665f` | `S1_llm_only` | `cites_advisory_number` | 2026/001 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/001 |
| `cand-c5d488d378858983` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-16T00:00:00Z | `fact-929541e916d3c7cc` | `fact-929541e916d3c7cc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160000-160000 |
| `cand-c8ab1566e3d17638` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-d0dbcdf471b89412` | `S1_llm_only` | `has_source_elevation` | 9455 FT AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 9455 FT AMSL |
| `cand-d86486a4e50b44e3` | `S1_llm_only` | `states_observed_volcanic_ash_cloud` | NOT PROVIDED | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: NOT PROVIDED |
| `cand-e1c7fd94debae5f5` | `S1_llm_only` | `is_in_area` | KAMCHATKA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA |
| `cand-e88bc7c2ec2db28b` | `S1_llm_only` | `states_forecast_volcanic_ash_cloud_plus_6_hours` | NOT PROVIDED | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/2100Z NOT PROVIDED |
| `cand-f2027cdf9be56ce8` | `S1_llm_only` | `states_observed_volcanic_ash_datetime` | NOT PROVIDED | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: NOT PROVIDED |

## ATCSCC-GOLD-088 / 2026-05-18:021

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=53, est=16 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 26
- Cross-system clusters: 26
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=21

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET EFFECTIVE TIME: 180507-180945 SIGNATURE: 26/05/18 05:07 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-13e40f2e41302060` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T09:45:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-088:fact-04-3e9d1bb57c6a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS... |
| `cand-23f22c9b0381ebd7` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T05:07:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-088:fact-02-05a2b129f481` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS... |
| `cand-29a66fccccd701dd` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 21 | `fact-6919f298bfb00e1e` | `S1b_llm_canonicalized:2026-05-18:021:fact-f2c700c7f666, fact-6919f298bfb00e1e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-3efe823de3e1ec57` | `S1_llm_only` | `element_type` | APT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-47f9add13d7fc6c6` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | OBJECTIVES MET | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-088:fact-02-f6a23e807a8b` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-5574c0597082b73b` | `S1_llm_only` | `advisory_time` | 0503Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-60f5bb49e3d14ecf` | `S2_llm_schema_slice` | `advisoryNumber` | 21 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-088:fact-01-0cef5d9f94b6` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS... |
| `cand-70eec77c13ad0f16` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `` | `S1b_llm_canonicalized:2026-05-18:021:fact-bea3bc4c9e42` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-746e81e209a25fec` | `S2_llm_schema_slice` | `initiativeComments` | OBJECTIVES MET | `` | `S2_llm_schema_slice:ATCSCC-GOLD-088:fact-07-1a15ccf02c52` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS... |
| `cand-8950bba896410d4b` | `S1_llm_only` | `announced_advisory_area` | SFO/ZOA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-8e1da0077d9d3634` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T05:07:00Z | `fact-fdba3e38f0e71541` | `fact-fdba3e38f0e71541` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180507-180945 |
| `cand-9ea24e3df8c233a6` | `S1_llm_only` | `ground_delay_program_status` | CNX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-a70627d46a9738c1` | `S1_llm_only` | `named_airport_element` | SFO | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-ab3bd42808a8cf0f` | `S1_llm_only` | `comment` | OBJECTIVES MET | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-b84942381cf3d2f0` | `S2_llm_schema_slice` | `impactingCondition` | other | `` | `S2_llm_schema_slice:ATCSCC-GOLD-088:fact-06-21f62f274743` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS... |
| `cand-bfee977774ad0d92` | `S1_llm_only` | `ground_delay_program_period` | 18/0503Z - 18/0845Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-c152438b1f916c03` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `fact-1208a5473b1c36ce` | `fact-1208a5473b1c36ce` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-c5a2fe167d9ad0bb` | `S1_llm_only` | `announced_advisory_topic` | CDM GROUND DELAY PROGRAM CNX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-db306c36ca46a977` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T05:07:00Z | `fact-e358ab2d1d580e1d` | `fact-e358ab2d1d580e1d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 05:07 |
| `cand-ddb905fd1e845152` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T05:07:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-088:fact-03-3eeef5ff1b33` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS... |
| `cand-e0d1107d83bbd155` | `S1_llm_only` | `instruction` | DISREGARD EDCTS FOR DEST SFO | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |
| `cand-e5a27602ea762e5e` | `S1_llm_only` | `effective_interval` | 180507-180945 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180507-180945 |
| `cand-f050227a1791a55d` | `S2_llm_schema_slice` | `controlledNASelement` | SFO | `` | `S2_llm_schema_slice:ATCSCC-GOLD-088:fact-05-354095d22295` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS... |
| `cand-f4357847596acd43` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | OBJECTIVES MET | `fact-46ed471a0f146fa6` | `fact-46ed471a0f146fa6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: OBJECTIVES MET |
| `cand-f5f8bd554146d954` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T09:45:00Z | `fact-3c6bc048f5d32370` | `fact-3c6bc048f5d32370` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180507-180945 |
| `cand-fe2ef636381314d5` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | SFO | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-088:fact-01-91d33a8ce06a` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0503Z GDP CNX PERIOD: 18/0503Z - 18/0845Z DISREGARD EDCTS FOR DEST SFO COMMENTS: OBJECTIVES MET |

## ATCSCC-GOLD-042 / 2026-05-20:015

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=51, est=16 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 25
- Cross-system clusters: 25
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=15

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. EFFECTIVE TIME: 200051-200330 SIGNATURE: 26/05/20 00:51 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-016190caeff7aea2` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-042:fact-03-8e4fc5521a1f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-039363b9ebc64800` | `S2_llm_schema_slice` | `initiativeComments` | ADVISORY 136 **EXTENDS TIME FOR L451 ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROU... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-042:fact-04-3645bb271c67` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-26bec8b9dde1754f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMA |
| `cand-2d32195c080d1450` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `fact-2b4d60a71f7f5783` | `fact-2b4d60a71f7f5783` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-36195c5046792989` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:51:00Z | `fact-096d3158051e36ef` | `fact-096d3158051e36ef` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200051-200330 |
| `cand-4672720305d9c15e` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 15 | `fact-679a8416786b3410` | `S1b_llm_canonicalized:2026-05-20:015:fact-b99b5d9cf8f7, fact-679a8416786b3410` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-4a3cde007ab37f78` | `S1_llm_only` | `states_effective_time` | 200051-200330 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200051-200330 |
| `cand-4f9253bf7c1f0e58` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-042:fact-02-53be943a503c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-5dcaf79b634f7855` | `S2_llm_schema_slice` | `advisoryNumber` | 15 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-042:fact-06-e7872870ac86` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-620ac2fcdb222f29` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteType` | ROUTE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-042:fact-02-088a8d2c0799` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-68a8dee020aa8665` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-042:fact-01-adb51b711581` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-6c1cc25fe8b0a1b2` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T00:51:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-042:fact-05-77025fc8aba9` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-88fe62fbf29655c9` | `S1_llm_only` | `replaces_advisory` | 136 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *REPLACES ADVISORY 136 |
| `cand-944e6de2e1b804fd` | `S2_llm_schema_slice` | `controlledNASelement` | ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-978d1008f2d343b8` | `S1_llm_only` | `has_advisory_identifier_text` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD |
| `cand-a33265f6f335284c` | `S1_llm_only` | `extends_time_for_route` | L451 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | **EXTENDS TIME FOR L451 |
| `cand-a3f27863bc67c9db` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T03:30:00Z | `fact-9930705089ce87a7` | `fact-9930705089ce87a7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200051-200330 |
| `cand-b20296e7c9e04e84` | `S1_llm_only` | `are_encouraged_to_file` | alternate routes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. |
| `cand-bd188c397a587ab3` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-042:fact-01-97a1b2124390` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-c58104ff8a8859b2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T00:51:00Z | `fact-d67f5c33389494a6` | `fact-d67f5c33389494a6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:51 |
| `cand-e368c03d5a2c92cc` | `S1_llm_only` | `advises_route_status` | L451 is closed due to thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA ADVISES THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-ea1fa272914e47c1` | `S1_llm_only` | `states_event_time` | 19/2200 - 20/0300Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/2200 - 20/0300Z |
| `cand-f166154bb65686f7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | ZMA | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-042:fact-04-f3858fd323b6` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |
| `cand-f9267fa950ffd9a1` | `S1_llm_only` | `has_constrained_facility` | ZMA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA |
| `cand-fb5fa533102b6fed` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteReason` | WEATHER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-042:fact-03-a53e2b4c59dd` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD MESSAGE: EVENT TIME: 19/2200 - 20/0300Z CONSTRAINED FACILITIES: ZMA *REPLACES ADVISORY 136 **EXTENDS TIME FOR L451 ZMA... |

## ATCSCC-GOLD-051 / 2026-05-14:030

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=51, est=17 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 25
- Cross-system clusters: 25
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=30

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA MESSAGE: FVXX21 KNES 140834 WSI DDS:140836 VA ADVISORY DTG: 20260514/0834Z VAAC: WASHINGTON VOLCANO: SANTA MARIA 342030 PSN: N1445 W09133 AREA: GUATEMALA SOURCE ELEV: 12287 FT AMSL ADVISORY NR: 2026/237 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: LGT VA EMS OBS VA DTG: 14/0800Z OBS VA CLD: SFC/FL140 N1446 W09133 - N1444 W09132 - N1437 W09139 - N1442 W09144 - N1446 W09133 MOV SW 5KT FCST VA CLD +6HR: 14/1400Z SFC/FL140 N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 FCST VA CLD +12HR: 14/2000Z SFC/FL140 N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 FCST VA CLD +18HR: 15/0200...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0cbb4d9299618c66` | `S1b_llm_canonicalized` | `advisoryNumber` | 30 | `` | `S1b_llm_canonicalized:2026-05-14:030:fact-523f49b68f98` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/237 |
| `cand-1f0306c10cc34a92` | `S1_llm_only` | `expects volcanic ash movement` | toward the SSW through T+6 then SW by T+12 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA MVMT EXP TWD THE SSW THRU T+6 THEN SW BY T+12. |
| `cand-22c7eed68e849857` | `S1_llm_only` | `has source elevation` | 12287 FT AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12287 FT AMSL |
| `cand-2604004e9b51dd91` | `S1_llm_only` | `states possible light volcanic ash emissions observed on satellite and webcam` | moving southwest from summit | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PSBL LGT VA EMS OBS ON STLT AND WEBCAM MVG SW FM SUMMIT. |
| `cand-276a67fda13a7ec1` | `S1_llm_only` | `states forecast basis` | webcam observations and NWP models | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FL BASED ON WEBCAM OBS, FCST BASED ON NWP MDLS. |
| `cand-34468c26c6098cab` | `S1_llm_only` | `was moving direction and speed` | southwest at 5 kt | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 5KT |
| `cand-39bb12da635e0bfd` | `S1_llm_only` | `was observed with vertical extent` | SFC/FL140 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: SFC/FL140 N1446 W09133 - N1444 W09132 - N1437 W09139 - N1442 W09144 - N1446 W09133 |
| `cand-39f545114ff62ee7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `fact-9f56f45557d37499` | `fact-9f56f45557d37499` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-4c632a4755579ef9` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 30 | `fact-2574a6df4b338005` | `S1b_llm_canonicalized:2026-05-14:030:fact-219a7921c09b, fact-2574a6df4b338005` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-51e505d0806f6f95` | `S1_llm_only` | `has information sources` | GOES-19, webcam, NWP models | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. |
| `cand-63cfdfc02d14adde` | `S1_llm_only` | `was observed at time` | 14/0800Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: 14/0800Z |
| `cand-711f77717755412a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `fact-0311cf408da466a3` | `fact-0311cf408da466a3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-90219569d8587832` | `S1_llm_only` | `forecast position at +12 hours` | SFC/FL140 near N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/2000Z SFC/FL140 N1446 W09133 - N1445 W09132 - N1428 W09143 - N1434 W09152 - N1446 W09133 |
| `cand-a01c426c457037c9` | `S2_llm_schema_slice` | `advisoryNumber` | 30 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-051:fact-01-b321ac034880` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 030 |
| `cand-a0529978e2816567` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - SANTA MARIA | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-a2bf3b5aa1aa0f78` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T08:34:00Z | `fact-6fdbebb0c85f48d3` | `fact-6fdbebb0c85f48d3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 08:36 |
| `cand-a411a33bf361a288` | `S1_llm_only` | `effective time window` | 140000-140000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140000-140000 |
| `cand-aee0f523944db02f` | `S1_llm_only` | `has eruption activity detail` | light volcanic ash emissions observed | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: LGT VA EMS OBS |
| `cand-b7db93ba1efe6090` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T08:36:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-051:fact-02-019831b68eab` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 08:36 |
| `cand-b8233ae37e8647a7` | `S1_llm_only` | `is located in area` | Guatemala | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: SANTA MARIA 342030 PSN: N1445 W09133 AREA: GUATEMALA |
| `cand-d7e6b778c5c05e8b` | `S1_llm_only` | `forecast position at +18 hours` | no volcanic ash expected | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/0200Z NO VA EXP |
| `cand-e29fdee288ac3baf` | `S1_llm_only` | `has advisory number` | 2026/237 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/237 |
| `cand-e57efb8af8879b6e` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - SANTA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-051:fact-03-6f918d244e92` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `cand-f03f2b5a04f1bbb6` | `S1_llm_only` | `forecast position at +6 hours` | SFC/FL140 near N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/1400Z SFC/FL140 N1446 W09133 - N1446 W09132 - N1423 W09131 - N1426 W09143 - N1446 W09133 |
| `cand-fdfa6d00e2ef62c6` | `S1_llm_only` | `has volcano advisory bulletin` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |

## ATCSCC-GOLD-071 / 2026-05-19:064

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=51, est=16 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 25
- Cross-system clusters: 25
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=64

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 19/1900 - 20/0200 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 191721-200230 SIGNATURE: 26/05/19 17:21 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b6f686876c34bec` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T17:21:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-16442a20053f4ab7` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:EWR | `` | `S1b_llm_canonicalized:2026-05-19:064:fact-006774ca9d9d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-1ad6df11ae7eabe8` | `S2_llm_schema_slice` | `controlledNASelement` | Newark Airport | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-1c7322638390caed` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T17:21:00Z | `fact-6f9e4220aa50e90f` | `fact-6f9e4220aa50e90f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 17:21 |
| `cand-448c8f20be23a401` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T02:30:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-54006c12e1482db6` | `S2_llm_schema_slice` | `initiativeComments` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-57121d971a7872cc` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T17:21:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-5e57a2a816cffc0d` | `S2_llm_schema_slice` | `impactingCondition` | volume | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-684f533ff555f3e0` | `S2_llm_schema_slice` | `advisoryNumber` | 64 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | EWR USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT OF UP TO 30 MINUTES DURING PERIODS OF COMPACTED DEMAND. |
| `cand-767d252d0fa6a790` | `S1_llm_only` | `names_constrained_facility` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-76cc9a52b41dfd26` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 64 | `fact-3890ee9863d22e48` | `S1b_llm_canonicalized:2026-05-19:064:fact-6c32d8c7b340, S2_llm_schema_slice:ATCSCC-GOLD-071:fact-01-0b48b15816c2, fact-3890ee9863d22e48` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-79c45a0168409193` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-81658e9ddcbff1e2` | `S1_llm_only` | `have_maximum_duration_of` | up to 30 minutes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OF UP TO 30 MINUTES |
| `cand-969e80405bf0a315` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T17:21:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-071:fact-02-a831c015f163` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-a03c4baa5ce4934f` | `S1_llm_only` | `states_updates_will_follow_if_necessary` | updates will follow if necessary | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-b158226f5f9defbd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `fact-9db8f8f637c0d550` | `fact-9db8f8f637c0d550` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191721-200230 |
| `cand-b5b37cbe2b9e10ca` | `S2_llm_schema_slice` | `controlledNASelement` | Newark Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-071:fact-06-fe3895708264` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-b5c551e652126b58` | `S1_llm_only` | `can_expect_arrival_delays_or_airborne_holding_into` | Newark Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AIRPORT |
| `cand-ba3dc218e5130a46` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T17:21:00Z | `fact-38a3e7f2a73939b4` | `fact-38a3e7f2a73939b4` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191721-200230 |
| `cand-c7c95258210da9cc` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T17:21:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-071:fact-03-bd2ba4bcc07d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-d55c3297e05cca71` | `S1_llm_only` | `gives_effective_time_window` | 191721-200230 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191721-200230 |
| `cand-e0ebb0c7643487b4` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T02:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-071:fact-04-cb37ed5f164f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-e2a144eb55430868` | `S1_llm_only` | `identifies_airport_delay_event_at` | EWR airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `cand-eac01ac6c89c14c1` | `S1_llm_only` | `occur_during` | periods of compacted demand | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DURING PERIODS OF COMPACTED DEMAND |
| `cand-eee17d730d4c4995` | `S2_llm_schema_slice` | `initiativeComments` | EWR AIRPORT ARRIVAL DELAYS | `` | `S2_llm_schema_slice:ATCSCC-GOLD-071:fact-05-a8ba3880a4a8` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |

## ATCSCC-GOLD-089 / 2026-05-16:018

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=51, est=17 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 25
- Cross-system clusters: 25
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=18

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION MESSAGE: EVENT TIME: 16/0915 - 17/0200 THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERPRETATION. EFFECTIVE TIME: 160909-170200 SIGNATURE: 26/05/16 09:09 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-112c742427a7bb1a` | `S1_llm_only` | `runs from` | 16/0915 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-2180ab82d6e2b4de` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-16T09:09:00Z | `fact-e28a6e34689931d2` | `fact-e28a6e34689931d2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160909-170200 |
| `cand-2187d7c3ede64a5b` | `S1_llm_only` | `should include` | call sign | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERP... |
| `cand-29d584dc630f730f` | `S1_llm_only` | `announces issue request page activation` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-2ba28bf90fdfe6ef` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-16T09:09:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-02-3a7903cef3ee` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 09:09 |
| `cand-38b10d04444616dc` | `S1_llm_only` | `should include` | position of flight | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERP... |
| `cand-4ac5c791e5d25323` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-16T09:15:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-03-706ce380ec4d` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-5a200bfb6ff9aac2` | `S2_llm_schema_slice` | `initiativeComments` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE R... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-08-110a1bf5fc1a` | `{"repaired_accepted": 1}` | `{}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERP... |
| `cand-696f9b21b7875a7c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-16T09:09:00Z | `fact-75b3c32009fc16f5` | `fact-75b3c32009fc16f5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 09:09 |
| `cand-718ae46f7899f3b3` | `S2_llm_schema_slice` | `initiativeComments` | THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-06-5c57ca0e3cff` | `{"repaired_accepted": 1}` | `{}` | THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. |
| `cand-908ed24cc012aaae` | `S1_llm_only` | `should include` | type of assistance requested | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERP... |
| `cand-914cadbbf58abf85` | `S1_llm_only` | `should send` | request messages to the page for resolution | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. |
| `cand-94e474a342fa80e3` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 18 | `fact-83e0ee9aa6cf510b` | `S1b_llm_canonicalized:2026-05-16:018:fact-0a9c746c1489, fact-83e0ee9aa6cf510b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-961deb74700c1f07` | `S1_llm_only` | `purpose` | to eliminate any misinterpretation | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERP... |
| `cand-b571f87b97c6d347` | `S1_llm_only` | `has advisory identifier` | 018 DCC 05/16/2026 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-c52fb2626696a34a` | `S1_llm_only` | `should include` | category of issue | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE ENSURE ADEQUATE INFORMATION IS PROVIDED IN REQUESTS SUCH AS CATEGORY OF ISSUE, CALL SIGN, POSITION OF FLIGHT, TYPE OF ASSISTANCE REQUESTED, ETC TO ELIMINATE ANY MISINTERP... |
| `cand-d2c1d4da2957005d` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-17T02:00:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-04-380c7aed140d` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-d523bcaee34d7f1b` | `S2_llm_schema_slice` | `advisoryNumber` | 18 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-01-816f28a6759a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `cand-d61e7bba6e3d5e3c` | `S1_llm_only` | `starts at` | 160909 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160909-170200 |
| `cand-dc03fb5f688b97b8` | `S1_llm_only` | `ends at` | 170200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 160909-170200 |
| `cand-dc9f0d89c9f2860a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T02:00:00Z | `fact-c82c9c62e59ed6cf` | `fact-c82c9c62e59ed6cf` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 160909-170200 |
| `cand-e1f2971163f70e9f` | `S1_llm_only` | `status` | now open | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE IS NOW OPEN. |
| `cand-e8c7da8442b0ec2a` | `S1_llm_only` | `runs until` | 17/0200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/0915 - 17/0200 |
| `cand-eb601e0cc92a74e0` | `S2_llm_schema_slice` | `initiativeComments` | WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-07-b33cc2a5ac75` | `{"repaired_accepted": 1}` | `{}` | WEB PAGE USERS SHOULD SEND THEIR REQUEST MESSAGES TO THE PAGE FOR RESOLUTION. |
| `cand-f6a7e276c2743530` | `S2_llm_schema_slice` | `initiativeComments` | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION | `` | `S2_llm_schema_slice:ATCSCC-GOLD-089:fact-05-1ea26df13d04` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |

## ATCSCC-GOLD-096 / 2026-05-15:087

- Batch: `batch_10`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_10.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=51, est=17 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 25
- Cross-system clusters: 25
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=87

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 152323 WSI DDS:152324 VA ADVISORY DTG: 20260515/2323Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/567 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: POSS VA EMS EST VA DTG: 15/2300Z EST VA CLD: SFC/FL150 N1428 W09053 - N1427 W09052 - N1422 W09101 - N1426 W09102 - N1428 W09053 MOV SW 5KT FCST VA CLD +6HR: 16/0500Z SFC/FL150 N1431 W09103 - N1428 W09052 - N1427 W09052 - N1425 W09104 - N1431 W09103 FCST VA CLD +12HR: 16/1100Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09108 - N1426 W09110 - N1429 W09053 FCST VA CLD +18HR: 16/1700Z NO VA EXP R...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-082d129f24bc37ee` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/1700Z |
| `cand-143eb272596d626d` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N1428 W09052 |
| `cand-1a772bccf3884462` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: POSS VA EMS |
| `cand-241c0c8a67d6c1d9` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/1100Z SFC/FL150 N1429 W09053 - N1427 W09052 - N1419 W09108 - N1426 W09110 - N1429 W09053 |
| `cand-328a4691d01e7428` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 |
| `cand-36cbbdfd3b3eee77` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 87 | `fact-307048fb01d9ac6a` | `S1b_llm_canonicalized:2026-05-15:087:fact-cdded64f3ae1, S2_llm_schema_slice:ATCSCC-GOLD-096:fact-01-6ab962a18ceb, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-096:fact-01-6ab962a18ceb, fact-307048fb01d9ac6a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 4}` | `{}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-3a4f53245e19c3d8` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO |
| `cand-4aea799006c29164` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 16/1700Z NO VA EXP |
| `cand-502435770c3b27f0` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-55ecfc9dc7a0c2d6` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: GUATEMALA |
| `cand-5724fe263a0ff0ca` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA FL/DIR BASED ON PREV VAA AND MDL GUIDANCE. |
| `cand-5cd72fec58edd750` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/0500Z |
| `cand-60b8be2a1892c726` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-6418973e2e434fc7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `fact-a4bb95d5a3193469` | `fact-a4bb95d5a3193469` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-67078c46e9f87fef` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-15T23:24:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-096:fact-02-cd60b5687a2f, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-096:fact-02-cd60b5687a2f` | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/15 23:24 |
| `cand-7454915df88c01ea` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T00:00:00Z | `fact-814752a7cbc15d40` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-096:fact-03-4c8d5f0aa909, fact-814752a7cbc15d40` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a37f568b70aa99d5` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-15T15:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-096:fact-04-ff9c80cd999c` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 150000-150000 |
| `cand-a99f2d5b72ccca28` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T23:23:00Z | `fact-2b71b3fdda79f14f` | `fact-2b71b3fdda79f14f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 23:24 |
| `cand-a9dc95d049862406` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 16/0500Z SFC/FL150 N1431 W09103 - N1428 W09052 - N1427 W09052 - N1425 W09104 - N1431 W09103 |
| `cand-b2ca41d4eb52ee11` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 5KT |
| `cand-c50156e4798cb94c` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS/CLDS NOT SEEN IN SAT AND WEBCAM DUE TO DENSE MET CLDS. |
| `cand-c6baef3137e877a2` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `` | `S2_llm_schema_slice:ATCSCC-GOLD-096:fact-03-7c71eb661417, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-096:fact-05-7c71eb661417` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-ca9024b8dfd626e3` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDL FCST W-LY AND WSW-LY WINDS THRU T+12HRS. |
| `cand-cdb319281a370043` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 16/1100Z |
| `cand-f3bde2ac2f6be599` | `S1_llm_only` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 15/2300Z |

## ATCSCC-GOLD-034 / 2026-05-14:055

- Batch: `batch_04`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_04.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=49, est=15 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 24
- Cross-system clusters: 24
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=55

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. EFFECTIVE TIME: 141513-142330 SIGNATURE: 26/05/14 15:13 FAA.gov Home \| Privacy Policy \| Web Polic...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0412cb0ba7805cb6` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-14T15:13:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-034:fact-03-2076759d3d5b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVE... |
| `cand-07777c06e2cad01f` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-14T23:30:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-034:fact-04-3c6d2c1e89f6` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVE... |
| `cand-0ab4b69b693a6577` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T15:13:00Z | `fact-5df19ec5ad3865f2` | `fact-5df19ec5ad3865f2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 15:13 |
| `cand-13cca3d00d0f14aa` | `S2_llm_schema_slice` | `advisoryNumber` | 55 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-24d9e06c586ce773` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-14T23:30:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141513-142330 |
| `cand-2cb32915c866a2c5` | `S1_llm_only` | `has_time_range` | 14/1513 - 14/2300 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/1513 - 14/2300 |
| `cand-3c9aca16c077e5a7` | `S1_llm_only` | `should_ensure_in_flight_plan_remarks` | DVRSN | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-4a975efaa5d7a3fc` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REM... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-034:fact-05-7120a7a5a29a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVE... |
| `cand-4b9053488e41d2ea` | `S1_llm_only` | `activated_diversion_recovery_tool_for` | SAN Diego Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. |
| `cand-4fc73c89477c6a93` | `S1_llm_only` | `must_include_in_flight_plan_remarks` | DVRSN | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN REMARKS OF DIVERTED AIRCRAFT. |
| `cand-50030bd537fef7d8` | `S1_llm_only` | `are_not_automatically_exempt_when` | ground delay program or ground stop in effect for destination airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-588b7cc844378469` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SAN | `` | `S1b_llm_canonicalized:2026-05-14:055:fact-496df15b9f8d` | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA |
| `cand-66d9e5009e57da86` | `S2_llm_schema_slice` | `initiativeComments` | THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN IS INCLUDED IN FLIGHT PLAN... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVERSION RECOVERY TOOL FOR SAN DIEGO AIRPORT. CUSTOMERS SHOULD ENSURE THAT DVRSN... |
| `cand-7d3891987879ba3f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 55 | `fact-d54c79edf02f7816` | `fact-d54c79edf02f7816` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| `cand-8d5b823bfaedb4eb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T15:13:00Z | `fact-bf2ad5e01d9f133e` | `fact-bf2ad5e01d9f133e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141513-142330 |
| `cand-9cbf640e2bce2f27` | `S1_llm_only` | `is_constrained_facility_for_event` | SAN Airport diversion recovery | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZLA |
| `cand-ad2787f599efece8` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-14T15:13:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-034:fact-02-59294808d4a1` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVE... |
| `cand-ae702a5847260507` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-14T23:30:00Z | `fact-73ef91e720bccbfd` | `fact-73ef91e720bccbfd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141513-142330 |
| `cand-b87e162627fa7f61` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T15:13:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/14 15:13 |
| `cand-c1e755a2762b5407` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-14T15:13:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 141513-142330 |
| `cand-c9a767a61f64d088` | `S1_llm_only` | `will_still_receive` | EDCT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE THAT IF THERE IS A GROUND DELAY PROGRAM OR GROUND STOP IN EFFECT FOR THE DESTINATION AIRPORT DIVERTED FLIGHTS ARE NOT AUTOMATICALLY EXEMPT AND WILL STILL RECEIVE AN EDCT. |
| `cand-ddc88cc74bbcd8be` | `S1_llm_only` | `will_close_at` | end of the event time specified in this advisory | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-df68fa755b8806fd` | `S1_llm_only` | `will_close_for` | SAN Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UNLESS OTHERWISE NOTIFIED, DIVERSION RECOVERY WILL CLOSE FOR SAN AIRPORT AT THE END OF THE EVENT TIME SPECIFIED IN THIS ADVISORY. |
| `cand-e367623cd654a911` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 55 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-034:fact-01-00ec49abeb9e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED MESSAGE: EVENT TIME: 14/1513 - 14/2300 CONSTRAINED FACILITIES: ZLA THE ATCSCC HAS ACTIVATED THE DIVE... |

## ATCSCC-GOLD-060 / 2026-05-17:050

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=49, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 24
- Cross-system clusters: 24
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=50

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 1814Z GS CNX PERIOD: 17/1814Z - 17/2020Z COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z EFFECTIVE TIME: 171815-172120 SIGNATURE: 26/05/17 18:17 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-07cb30e36f6c3216` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T21:20:00Z | `fact-e8149e0d8aaf28a7` | `fact-e8149e0d8aaf28a7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171815-172120 |
| `cand-21fa77b3d9302310` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T18:17:00Z | `fact-d5d1c2a5d68ca309` | `fact-d5d1c2a5d68ca309` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 18:17 |
| `cand-2396102cda51b834` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-17T20:20:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-060:fact-06-d43667f5fded` | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 17/1814Z - 17/2020Z |
| `cand-3498ee0b686aee57` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-17T18:14:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-060:fact-04-c2041b2ba502` | `{"repaired_accepted": 1}` | `{}` | ADL TIME: 1814Z |
| `cand-4329e715a9087238` | `S1_llm_only` | `names_control_element` | DCA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-45835fd4e0719059` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-060:fact-01-ee6dfc4ecb99` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA ELEMENT TYPE: APT |
| `cand-5585191f084faa37` | `S1_llm_only` | `has_advisory_header` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX |
| `cand-55afa3a8e586b33e` | `S1_llm_only` | `states_effective_time_window` | 171815-172120 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171815-172120 |
| `cand-5680bb1f11ee5241` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADL | `` | `S1b_llm_canonicalized:2026-05-17:050:fact-5c26e921d6ae` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-5a1a2631e590e5cf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T18:15:00Z | `fact-8561fa01677ffe2a` | `fact-8561fa01677ffe2a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171815-172120 |
| `cand-6410382993468f6f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:APT | `` | `S1b_llm_canonicalized:2026-05-17:050:fact-51ca05f6a7eb` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-64217ab06008603f` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `fact-16ddc1cca832d902` | `S1b_llm_canonicalized:2026-05-17:050:fact-d61e3c040407, fact-16ddc1cca832d902` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: DCA |
| `cand-67e6099c84f011a8` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'label': 'DCA', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 1814Z GS CNX PERIOD: 17/1814Z - 17/2020Z COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-687642ff13595085` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-17T18:14:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-060:fact-05-025670412d89` | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 17/1814Z - 17/2020Z |
| `cand-6fae7db178709c59` | `S2_llm_schema_slice` | `initiativeComments` | EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-060:fact-07-895ed52d5319` | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-8059fdfca00f7fd4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z | `fact-afbbc5df0fe0778c` | `fact-afbbc5df0fe0778c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-85160164bc2c9ca9` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 50 | `fact-852ea5a1cafc1477` | `S1b_llm_canonicalized:2026-05-17:050:fact-717f8f266b23, fact-852ea5a1cafc1477` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX |
| `cand-86b62eb0dc305f2b` | `S1_llm_only` | `reports_ground_stop_cancellation` | GS CNX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-8e077e929993666e` | `S1_llm_only` | `defines_effective_period` | 17/1814Z - 17/2020Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 17/1814Z - 17/2020Z |
| `cand-929b6d7ed54001ea` | `S2_llm_schema_slice` | `impactingCondition` | other | `` | `S2_llm_schema_slice:ATCSCC-GOLD-060:fact-03-0183eea8e1a5` | `{"repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-9bd1d506b2ce5350` | `S2_llm_schema_slice` | `extensionProbability` | NONE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-060:fact-02-76eab402da86` | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 17/1814Z - 17/2020Z |
| `cand-a0b3f974528ba2d1` | `S1_llm_only` | `warns_of_increased_scheduling_delays` | aircraft within 1st tiers until 2000Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: EXPECT INCREASED SCHEDULING DELAYS FOR AIRCRAFT WITHIN 1ST TIERS UNTIL 2000Z |
| `cand-efbf193a7d307464` | `S1_llm_only` | `states_control_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-fd432e92fa75a58a` | `S1_llm_only` | `states_advisory_time` | 1814Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1814Z |

## ATCSCC-GOLD-063 / 2026-05-16:035

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=49, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 24
- Cross-system clusters: 24
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=35

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 161303-161830 SIGNATURE: 26/05/16 13:03 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0f62396c2e18bf29` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-16T13:03:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-063:fact-03-9cbdcd6ff9b0` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-1a7821ead6140d58` | `S2_llm_schema_slice` | `extensionProbability` | NONE | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ORD AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-1f5dde71e1dd73c5` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-16T13:03:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-063:fact-02-e42a50e4083b` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 13:03 |
| `cand-207f4906ada6986f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-16T13:03:00Z | `fact-2294ca205b7502da` | `fact-2294ca205b7502da` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 13:03 |
| `cand-3c0f298ccfc82525` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ORD AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-58cfc2ea860fe39a` | `S2_llm_schema_slice` | `advisoryNumber` | 35 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE... |
| `cand-5ed02143c4e4f8cc` | `S1_llm_only` | `can_expect` | arrival delays | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-6038489c7d015554` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-16T13:03:00Z | `fact-4447c667487b446c` | `fact-4447c667487b446c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-64746e84c5d68c89` | `S1_llm_only` | `event_time_window` | 16/1300 - 16/1800 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1300 - 16/1800 |
| `cand-6c4f9910924f2a05` | `S1_llm_only` | `caused_by` | thunderstorms | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_object_class": 1, "unknown_predicate": 1, "unknown_s...` | ...OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-78d812053b4767d0` | `S1_llm_only` | `will_follow_up_with` | updates if necessary | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-82a02dbdf01ea3db` | `S1_llm_only` | `announces` | ORD airport arrival delays | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS |
| `cand-954223c6c8ab82ee` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 35 | `fact-c98d07a8ff5fc416` | `S1b_llm_canonicalized:2026-05-16:035:fact-941798a62505, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-063:fact-01-9be7e20610c9, fact-c98d07a8ff5fc416` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS |
| `cand-b2f2b596fab11ce7` | `S1_llm_only` | `applies_to_airspace_or_users` | ZAU users | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT |
| `cand-bc9276b0a02709f2` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-16T18:30:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-063:fact-04-78fac5088929` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-c0f518cb4c333e67` | `S1_llm_only` | `maximum_duration` | up to 30 minutes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES |
| `cand-c706c3c2b4726267` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-16T13:03:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE... |
| `cand-c73b910b3f3b9532` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-16T18:30:00Z | `fact-187f338f404de787` | `fact-187f338f404de787` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161303-161830 |
| `cand-c86b55d842dd4a1a` | `S2_llm_schema_slice` | `initiativeComments` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOL... | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE... |
| `cand-d98d5011d5725bc8` | `S2_llm_schema_slice` | `controlledNASelement` | O'Hare Airport | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ORD AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-e1b35f0ea45df78d` | `S1_llm_only` | `can_expect` | airborne holding into O'Hare Airport up to 30 minutes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-e3a4490d9c740f91` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | ZAU users can expect arrival delays / airborne holding into the O'Hare airport of up to 30 minutes due to thunderstorms. Updates will fol... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-063:fact-05-d26f4443c7c1` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE O'HARE AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UP... |
| `cand-e42c83c71d659817` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-16T18:30:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS ... MESSAGE: EVENT TIME: 16/1300 - 16/1800 CONSTRAINED FACILITIES: ZAU USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE... |
| `cand-ed5be3908be8c64e` | `S1_llm_only` | `effective_time_window` | 161303-161830 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161303-161830 |

## ATCSCC-GOLD-079 / 2026-05-15:051

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=49, est=15 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 24
- Cross-system clusters: 24
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=51

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 15/1300 - 15/2000 CONSTRAINED FACILITIES: ZMA ZNY ***REPLACES ADVZY 049*** *L453/L455 END TIME EXTENDED* *L451 CONSTRAINED FACILITY MODIFIED* ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. USERS SHOULD FILE ALTERNATE ROUTING. EFFECTIVE TIME: 151735-152030 SIGNATURE: 26/05/15 17:35 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0168aaba8919839b` | `S2_llm_schema_slice` | `controlledNASelement` | L451 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-11-2a7456d7198d` | `{"repaired_accepted": 1}` | `{}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-07961a6b162661fe` | `S1_llm_only` | `end time extended` | extended end time | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *L453/L455 END TIME EXTENDED* |
| `cand-100d593ab09283c5` | `S1_llm_only` | `constrained facility modified` | modified constrained facility | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | *L451 CONSTRAINED FACILITY MODIFIED* |
| `cand-13b01d44989c1871` | `S1_llm_only` | `replaces` | ADVZY 049 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ***REPLACES ADVZY 049*** |
| `cand-1506bb818b7c753d` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteType` | ROUTE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-04-25691ecd31ee, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-079:fact-02-a2732958e02d` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-1be9b24ff1502d3e` | `S1_llm_only` | `is closed due to thunderstorms` | closure | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-270f93af1d14c1d7` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-08-d0a0c265fc51` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-2eac6bfa141cc107` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-15T17:35:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-07-5ac5b5814241` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-4285b224004cf0b2` | `S2_llm_schema_slice` | `initiativeComments` | L453/L455 END TIME EXTENDED | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-06-8b67e2ca6711` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-5f3173d5941335ef` | `S1b_llm_canonicalized` | `advisoryNumber` | 51 | `` | `S1b_llm_canonicalized:2026-05-15:051:fact-eb561f7d8ca0` | `{"repaired_accepted": 1}` | `{}` | ***REPLACES ADVZY 049*** |
| `cand-6913f3bf230a6f30` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `fact-60705d065c893710` | `fact-60705d065c893710` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-83293984f016a839` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `fact-cd310f901cfa90be` | `fact-cd310f901cfa90be` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151735-152030 |
| `cand-972492669025edf3` | `S2_llm_schema_slice` | `controlledNASelement` | L453 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-09-ae02aea3769f` | `{"repaired_accepted": 1}` | `{}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-9de072510e4254ef` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T17:35:00Z | `fact-9e0445ea6b25f3ff` | `fact-9e0445ea6b25f3ff` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151735-152030 |
| `cand-a23bd29d936030ce` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T17:35:00Z | `fact-f70f113ceb32cd2d` | `fact-f70f113ceb32cd2d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 17:35 |
| `cand-bd2fddba03353b79` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-15T17:35:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-02-fbd6caebd6e0, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-079:fact-05-21b29f5f74ec` | `{"repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-c3ac286e07a70400` | `S1_llm_only` | `should file alternate routing` | alternate routing | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FILE ALTERNATE ROUTING. |
| `cand-c5fc66fe91796f85` | `S1_llm_only` | `is constrained to` | 15/1300 - 15/2000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 15/1300 - 15/2000 |
| `cand-c71e79f4fd9987c1` | `S1_llm_only` | `are closed due to thunderstorms` | closure | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. |
| `cand-cf212174f8b07378` | `S2_llm_schema_slice` | `controlledNASelement` | L455 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-10-09072ea815e5` | `{"repaired_accepted": 1}` | `{}` | ZNY ADVISES THAT L453 AND L455 ARE CLOSED DUE TO THUNDERSTORMS. ZMA/ZNY ADVISE THAT L451 IS CLOSED DUE TO THUNDERSTORMS. |
| `cand-db297ea2a0eae7ef` | `S1_llm_only` | `is` | 151735-152030 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151735-152030 |
| `cand-f04309e9fee424ce` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-03-97cc94081645, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-079:fact-01-32460b8e817b` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-f26f1cecc4b8bc3b` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 51 | `fact-6c701710a5cce2f9` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-01-ff25d52048a2, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-079:fact-04-d5d424795685, fact-6c701710a5cce2f9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-f4e7cd872a8b74b2` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-079:fact-05-6ae1cb9901c2, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-079:fact-03-41a5dab381b0` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |

## ATCSCC-GOLD-087 / 2026-05-18:107

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=49, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 24
- Cross-system clusters: 24
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=107

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. EFFECTIVE TIME: 181933-190230 SIGNATURE: 26/05/18 19:33 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0efa9e5cec18810a` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'label': 'DENVER AIRPORT', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-1602c895f66ad6fb` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T02:30:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE S... |
| `cand-2653f921c60e0622` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-2ebcd1cfcf91d81a` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES. |
| `cand-38ce9629e5ec291d` | `S1_llm_only` | `states_expected_delay_for` | DENVER AIRPORT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-4539f375007409e5` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-18T19:33:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 19:33 |
| `cand-4b3eddb8230dc7b3` | `S1_llm_only` | `describes_event_time` | 18/2045 - 19/0200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/2045 - 19/0200 |
| `cand-54f4ed5c5d267c84` | `S1_llm_only` | `states_affected_departure_airports_scope` | departure airports within the first tier facilities | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES |
| `cand-55116fa027f5c714` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T02:30:00Z | `fact-f70ef046605642c1` | `fact-f70ef046605642c1` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181933-190230 |
| `cand-614c3525e309a517` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:FIRST | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES |
| `cand-6ac709f53bc51830` | `S1_llm_only` | `applies_to_center` | ZDV | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-6e8f89641f2f8189` | `S2_llm_schema_slice` | `initiativeComments` | ZDV users can expect TBFM / CALL-FOR-RELEASE scheduling delays to Denver Airport of 30 to 45 minutes from departure airports within the f... | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE S... |
| `cand-7bbd9d3d59da59dd` | `S1_llm_only` | `identifies_constrained_facilities` | ZDV | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-887f7319dc183b29` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T19:33:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE S... |
| `cand-91700a75a88dc84d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T19:33:00Z | `fact-eb0efb535061c4eb` | `fact-eb0efb535061c4eb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 19:33 |
| `cand-9399bf0008fcfc51` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T19:33:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS \| MESSAGE: EVENT TIME: 18/2045 - 19/0200 CONSTRAINED FACILITIES: ZDV USERS CAN EXPECT TBFM / CALL-FOR-RELEASE S... |
| `cand-9e5edede9f38e4c2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T19:33:00Z | `fact-2712d9aed92e8a53` | `fact-2712d9aed92e8a53` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181933-190230 |
| `cand-a79a2dc81d0cb144` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:TIER | `` | `S1b_llm_canonicalized:2026-05-18:107:fact-7104d81ac1c7` | `{"repaired_accepted": 1}` | `{}` | FROM DEPARTURE AIRPORTS WITHIN THE FIRST TIER FACILITIES |
| `cand-b580893c453f2d39` | `S1_llm_only` | `has_advisory_type` | DEN airport scheduling delays | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-b62315c345108859` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 107 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-bf1db667bb3d6424` | `S1_llm_only` | `states_effective_time` | 181933-190230 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181933-190230 |
| `cand-db10d1cfb5781f3c` | `S1_llm_only` | `states_delay_type` | TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |
| `cand-ec55f7cd15ea3061` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 107 | `fact-c063930bfc378e0e` | `S1b_llm_canonicalized:2026-05-18:107:fact-5d196b3619fa, fact-c063930bfc378e0e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `cand-f6cfd4e254a9485c` | `S1_llm_only` | `states_delay_duration_range` | 30 TO 45 MINUTES | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT TBFM / CALL-FOR-RELEASE SCHEDULING DELAYS TO DENVER AIRPORT OF 30 TO 45 MINUTES |

## ATCSCC-GOLD-076 / 2026-05-20:013

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=47, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 23
- Cross-system clusters: 23
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=13

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08ec29af2218658b` | `S1_llm_only` | `'names_controlled_element'}` | {'label': 'ORD ELEMENT', 'type': 'controlled_element'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-0efe226431af91e2` | `S1_llm_only` | `'has_advisory_identifier'}` | {'label': 'ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX', 'type': 'advisory_identifier'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX |
| `cand-163645cc55da5397` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 13 | `fact-be74c0e8a08ced21` | `S1b_llm_canonicalized:2026-05-20:013:fact-cd7a1fecbbe4, fact-be74c0e8a08ced21` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX |
| `cand-17730891bca1a550` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | ORD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-076:fact-01-71df1fcdaacd` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-1b2f715532a913a9` | `S2_llm_schema_slice` | `extensionProbability` | NONE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-076:fact-02-0a0fc0d5e82e` | `{"repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 20/0044Z - 20/0548Z |
| `cand-29bd5cb368868828` | `S2_llm_schema_slice` | `initiativeComments` | GS CNX PERIOD: 20/0044Z - 20/0548Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-076:fact-03-74be9a4348b4` | `{"repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 |
| `cand-3af5001987f775ab` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `fact-0d4dbd4e1d428084` | `fact-0d4dbd4e1d428084` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-3e721474c68fbf70` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T00:06:48Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-076:fact-06-9c72bb6a2c23` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-6939c5284c8e72d5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-b7e1452d859d8a65` | `fact-b7e1452d859d8a65` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 200045-200648 SIGNATURE: 26/05/20 00:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-73bfe796d151fa34` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T00:44:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-076:fact-04-22ee4f99ef8f` | `{"repaired_accepted": 1}` | `{}` | ADL TIME: 0044Z |
| `cand-78970ed82da97f44` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T06:48:00Z | `fact-5ca14e93c8cfc564` | `fact-5ca14e93c8cfc564` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-7b39fbc33d02d1ed` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | NONE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-076:fact-02-77f68d9d8d0a` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX |
| `cand-818c2d7314543be4` | `S1_llm_only` | `'states_ground_stop_cancellation_time'}` | {'label': '0044Z', 'type': 'time_value'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-9a9b1638c94d811f` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T00:04:45Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-076:fact-05-a88a71c9288e` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-9f4d2096944328ff` | `S1_llm_only` | `'was_signed_at'}` | {'label': '26/05/20 00:46', 'type': 'signature_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 00:46 |
| `cand-ad4d167da1930cb8` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-20T00:46:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-076:fact-04-9da6617e048d` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:46 |
| `cand-adf9a8956e5029b3` | `S1_llm_only` | `'has_effective_time'}` | {'label': '200045-200648', 'type': 'effective_time_range'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200045-200648 |
| `cand-b0bfa9c9799ac2f7` | `S1_llm_only` | `'states_ground_stop_cancellation_period'}` | {'label': '20/0044Z - 20/0548Z', 'type': 'time_period'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-bedbf9754a65c364` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T00:46:00Z | `fact-a6510ea656adf9b7` | `fact-a6510ea656adf9b7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:46 |
| `cand-e32f92a07080a8e9` | `S2_llm_schema_slice` | `controlledNASelement` | ORD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-076:fact-01-d9c64faffda0` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT |
| `cand-edfe6cc56a908314` | `S1_llm_only` | `'has_element_type'}` | {'label': 'APT ADL', 'type': 'element_type'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 0044Z GS CNX PERIOD: 20/0044Z - 20/0548Z COMMENTS: |
| `cand-eee7f7d4cab1b065` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:45:00Z | `fact-bc7c92b4f2d4c61b` | `fact-bc7c92b4f2d4c61b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200045-200648 |
| `cand-fc9cd34778b7511d` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | GS CNX PERIOD: 20/0044Z - 20/0548Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-076:fact-03-72d7cf883b97` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | GS CNX PERIOD: 20/0044Z - 20/0548Z |

## ATCSCC-GOLD-083 / 2026-05-20:016

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=47, est=14 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 23
- Cross-system clusters: 23
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=16

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT: LGA AND JFK RELEASED FACILITIES: ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA REMARKS: DAL AND SUBS GS CX. EFFECTIVE TIME: 200052-200200 SIGNATURE: 26/05/20 00:52 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-12ae48ce67c06682` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:52:00Z | `fact-3467ee39badb9c19` | `fact-3467ee39badb9c19` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200052-200200 |
| `cand-1ed5b5ffc465b0f5` | `S2_llm_schema_slice` | `advisoryNumber` | 16 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-01-b1f6145f95e1` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT:... |
| `cand-2a83e8ddedcf5db1` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-04-c2b51a3d3a3e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT:... |
| `cand-38f76ca4c0d28cb9` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T00:52:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-02-038df9913ebe` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT:... |
| `cand-3cc591c711d9e7b4` | `S2_llm_schema_slice` | `impactingCondition` | other | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-06-ec0f20b40a80` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT:... |
| `cand-4b256368ea715446` | `S2_llm_schema_slice` | `extensionProbability` | NONE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-05-a9a79ac7137b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT:... |
| `cand-4ed9d5a733937e7c` | `S1_llm_only` | `'LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS'}` | {'label': 'ground stop cancellation for DAL and subsidiaries', 'text': 'LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-526f96105bdfd5cb` | `S1_llm_only` | `'05/20/2026'}` | {'label': '2026-05-20', 'text': '05/20/2026'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-5b0bc4c27c60d7e6` | `S3_llm_schema_slice_validator_repair` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-5f56e012290c2d50` | `S2_llm_schema_slice` | `initiativeComments` | DAL AND SUBS GS CX. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-07-230fa7c159a9` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT:... |
| `cand-60600f39b67b1d6f` | `S2_llm_schema_slice` | `withinARTCC` | ZNY | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-08-c10acfe4dc8b, S2_llm_schema_slice:ATCSCC-GOLD-083:fact-09-c10acfe4dc8b` | `{"repaired_accepted": 2}` | `{}` | DESTINATION AIRPORT: LGA AND JFK |
| `cand-6f9bf4ed630ff433` | `S1_llm_only` | `'20/0050 - 20/0130'}` | {'label': 'event time window', 'text': '20/0050 - 20/0130'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/0050 - 20/0130 |
| `cand-9b746ed1110235c7` | `S2_llm_schema_slice` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-a9a184899df24153` | `S1_llm_only` | `'200052-200200'}` | {'label': 'effective time window', 'text': '200052-200200'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200052-200200 |
| `cand-af97dfcc33e30d46` | `S3_llm_schema_slice_validator_repair` | `unmapped_payload` |  | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-b1bd1861f54c67f2` | `S1_llm_only` | `'LGA AND JFK'}` | {'label': 'LGA and JFK', 'text': 'LGA AND JFK'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DESTINATION AIRPORT: LGA AND JFK |
| `cand-bbc29b2bfa06bae6` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T02:00:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-083:fact-03-7e0081e6381c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS MESSAGE: EVENT TIME: 20/0050 - 20/0130 CONSTRAINED FACILITIES: ZNY DESTINATION AIRPORT:... |
| `cand-d01eed29cbdb034c` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 16 | `fact-7a389ab9761eaa16` | `S1b_llm_canonicalized:2026-05-20:016:fact-5f2ba44656a2, fact-7a389ab9761eaa16` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `cand-d2a39e6fd8bab368` | `S1_llm_only` | `'ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA'}` | {'label': 'released facilities list', 'text': 'ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RELEASED FACILITIES: ZSE, ZOA, ZLA, ZAB, ZLC, ZDV, ZKC, ZFW, ZME, ZHU, ZMA |
| `cand-eb197e85d719967a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T02:00:00Z | `fact-7f9d3ebebc636d47` | `fact-7f9d3ebebc636d47` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200052-200200 |
| `cand-ed84a9ec32b55b05` | `S1_llm_only` | `'ZNY'}` | {'label': 'ZNY', 'text': 'ZNY'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-f76295299b384250` | `S1_llm_only` | `'DAL AND SUBS GS CX.'}` | {'label': 'ground stop cancellation for DAL and subsidiaries', 'text': 'DAL AND SUBS GS CX.'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: DAL AND SUBS GS CX. |
| `cand-f92cdeb325d0f5bf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T00:52:00Z | `fact-2656b5c4f0f1a6ef` | `fact-2656b5c4f0f1a6ef` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:52 |

## ATCSCC-GOLD-078 / 2026-05-20:026

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=45, est=15 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 22
- Cross-system clusters: 22
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=26

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 200158 WSI DDS:200159 VA ADVISORY DTG: 20260520/0158Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/584 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 20/0140Z EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 MOV SW 10KT FCST VA CLD +6HR: 20/0730Z SFC/FL150 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 FCST VA CLD +18HR: 20/1930Z SFC/FL1...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0a68dd55dbaa6dff` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `fact-abe663e6897f67d8` | `fact-abe663e6897f67d8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-176659542d76057e` | `S1_llm_only` | `estimated_vertical_extent` | SFC/FL140 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 20/1330Z SFC/FL140 N1428 W09053 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09053 |
| `cand-1ca6b0533f551ca7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T01:58:00Z | `fact-4c4774c908371d7d` | `fact-4c4774c908371d7d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 02:00 |
| `cand-1d51e7e709980eb4` | `S1_llm_only` | `estimated_time_of_detection` | 20/0140Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 20/0140Z |
| `cand-486c0c3e4abe4e6f` | `S1_llm_only` | `has_advisory_topic` | Volcanic Activity Bulletin - Fuego | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-7098edfa28584c04` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T20:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-7387a9faa3e4ad0e` | `S1_llm_only` | `movement_direction_and_speed` | SW 10KT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-76382fac220c5a30` | `S1_llm_only` | `has_advisory_region` | Guatemala | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-83f71483dd9fc06c` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 26 | `fact-0235544ddd8026a3` | `S1b_llm_canonicalized:2026-05-20:026:fact-65d44deb1c0a, fact-0235544ddd8026a3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-879e41ac3369ffd5` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T02:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 02:00 |
| `cand-92b9278b9a69e678` | `S1_llm_only` | `forecast_change` | No change forecast for next 18 hours | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-968eaa9db625c547` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-9c2bdcfdf386f396` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T20:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-9c57371426f54d28` | `S1_llm_only` | `estimated_vertical_extent` | SFC/FL140 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/1930Z SFC/FL140 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1424 W09104 - N1428 W09052 |
| `cand-a40908d03115aac4` | `S1_llm_only` | `likely_to_continue` | Likely continue given recent activity | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-abaa368ca28ddb80` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `fact-328de4ade0096b70` | `fact-328de4ade0096b70` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-b735f72d7ea8f240` | `S1_llm_only` | `estimated_vertical_extent` | SFC/FL150 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/0730Z SFC/FL150 N1428 W09052 - N1427 W09052 - N1420 W09101 - N1423 W09103 - N1428 W09052 |
| `cand-bd07ff4bb2517f5d` | `S1_llm_only` | `estimated_vertical_extent` | SFC/FL140 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 N1428 W09052 - N1428 W09052 - N1420 W09101 - N1423 W09104 - N1428 W09052 |
| `cand-c081dd7cc11c407a` | `S2_llm_schema_slice` | `advisoryNumber` | 26 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-db1ec6bbb3891310` | `S1_llm_only` | `identifies_eruption_details` | Ongoing | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING |
| `cand-e5940e801f28378c` | `S1_llm_only` | `not_detected_by` | Satellite due to weather clouds in summit area | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-fbe5166f844e52e0` | `S1_llm_only` | `has_source_elevation` | 12346 FT AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |

## ATCSCC-GOLD-075 / 2026-05-18:119

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=43, est=15 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 21
- Cross-system clusters: 21
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=119

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE MESSAGE: FVXX22 KNES 182009 WSI DDS:182010 VA ADVISORY DTG: 20260518/2009Z VAAC: WASHINGTON VOLCANO: PURACE 351060 PSN: N0219 W07624 AREA: COLOMBIA SOURCE ELEV: 15256 FT AMSL ADVISORY NR: 2026/083 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: PSBL VA EMS EST VA DTG: 18/1940Z EST VA CLD: SFC/FL180 N0225 W07629 - N0219 W07623 - N0219 W07623 - N0223 W07632 - N0225 W07629 MOV NW 20KT FCST VA CLD +6HR: 19/0130Z SFC/FL180 N0226 W07629 - N0219 W07623 - N0219 W07624 - N0223 W07632 - N0226 W07629 FCST VA CLD +12HR: 19/0730Z NO VA EXP FCST VA CLD +18HR: 19/1330Z NO VA EXP RMK: VA NOT DETECTED IN STLT IMG. VA EMS MAY CONT. MDL GUIDANCE SUGGESTS...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0010ad2874a69a66` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T00:00:00Z | `fact-8492eb2a12f2afd1` | `fact-8492eb2a12f2afd1` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-00c3a173919e8609` | `S1_llm_only` | `'did not detect volcanic ash'}` | {'label': 'VA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED IN STLT IMG. |
| `cand-1c19d9d0596b5f3e` | `S1_llm_only` | `'forecast status'}` | {'label': 'SFC/FL180'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/0130Z SFC/FL180 |
| `cand-39cc59e3e8310259` | `S1_llm_only` | `'advisory number'}` | {'label': '2026/083'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/083 |
| `cand-4eaefd6bd96610fd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T20:09:00Z | `fact-2ac31d350274c758` | `fact-2ac31d350274c758` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:10 |
| `cand-4ec4c0d9aea78d3f` | `S1b_llm_canonicalized` | `advisoryNumber` | 119 | `` | `S1b_llm_canonicalized:2026-05-18:119:fact-4b40c67adddb` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/083 |
| `cand-54b5c633c4c7955d` | `S1_llm_only` | `'may continue'}` | {'label': 'CONT.'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS MAY CONT. |
| `cand-59fa28089b3303df` | `S1_llm_only` | `'source elevation'}` | {'label': '15256 FT AMSL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 15256 FT AMSL |
| `cand-6ffbf1e2edf6a2ab` | `S1_llm_only` | `'estimated ash cloud top and base'}` | {'label': 'SFC/FL180'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: PSBL VA EMS EST VA DTG: 18/1940Z EST VA CLD: SFC/FL180 |
| `cand-81e0a657db44413c` | `S1_llm_only` | `'is'}` | {'label': 'LOW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST CONFIDENCE LOW. |
| `cand-86a823de1e641135` | `S1_llm_only` | `'located in area'}` | {'label': 'COLOMBIA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: COLOMBIA |
| `cand-8905281493295ada` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 119 | `fact-62ff592e811600f9` | `S1b_llm_canonicalized:2026-05-18:119:fact-383091235c6e, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-075:fact-01-3940943f4e48, fact-62ff592e811600f9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-8bda81516171d93a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T00:00:00Z | `fact-320ebfdda63b3187` | `fact-320ebfdda63b3187` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-a3c35652f9ed80b4` | `S1_llm_only` | `'movement speed'}` | {'label': '20KT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 20KT |
| `cand-a9453ff053a88a68` | `S1_llm_only` | `'forecast status'}` | {'label': 'NO VA EXP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 19/1330Z NO VA EXP |
| `cand-b496478e62e8540b` | `S1_llm_only` | `'reports volcano'}` | {'label': 'PURACE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: PURACE 351060 |
| `cand-b71a05de1b9b0e4f` | `S1_llm_only` | `'forecast status'}` | {'label': 'NO VA EXP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/0730Z NO VA EXP |
| `cand-d193538dfe43da22` | `S1_llm_only` | `'has advisory title'}` | {'label': 'VOLCANIC ACTIVITY BULLETIN - PURACE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-d5836a4cc3568acc` | `S1_llm_only` | `'suggests movement through'}` | {'label': 'NW MVMT THRU T+6'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MDL GUIDANCE SUGGESTS NW MVMT THRU T+6. |
| `cand-e1b0219a7d467c73` | `S1_llm_only` | `'moves toward'}` | {'label': 'NW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 20KT |
| `cand-ebd5fbc6392186b1` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - PURACE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-075:fact-02-cf2cd718f5e8` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |

## ATCSCC-GOLD-049 / 2026-05-19:013

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=41, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 20
- Cross-system clusters: 20
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=13

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL MESSAGE: FVXX24 KNES 190606 WSI DDS:190609 VA ADVISORY DTG: 20260519/0606Z VAAC: WASHINGTON VOLCANO: POPOCATEPETL 341090 PSN: N1901 W09837 AREA: MEXICO SOURCE ELEV: 17693 FT AMSL ADVISORY NR: 2026/196 INFO SOURCE: GOES-19. WEBCAM. ERUPTION DETAILS: VA EMS ENDED OBS VA DTG: 19/0551Z OBS VA CLD: VA NOT IDENTIFIABLE FM STLT DATA FCST VA CLD +6HR: 19/1200Z NO VA EXP FCST VA CLD +12HR: 19/1800Z NO VA EXP FCST VA CLD +18HR: 20/0000Z NO VA EXP RMK: VA NOT DETECTED ON VARIOUS STLT PRODUCTS. WEBCAM SHOWS ONLY STEAM/GAS EMS CURRENTLY. NEW VA EMS LIKELY AT ANY TIME. ...KONON EFFECTIVE TIME: 190000-190000 SIGNATURE: 26/05/19 06:09 FAA.gov Home \|...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02f1d920ea9e662d` | `S1_llm_only` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '19/1800Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 19/1800Z NO VA EXP |
| `cand-059b1a847219f77d` | `S1_llm_only` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '20/0000Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 20/0000Z NO VA EXP |
| `cand-108d2f7f17640892` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 13 | `fact-233e5df1a30aafcb` | `fact-233e5df1a30aafcb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-16093312a035c2f5` | `S1_llm_only` | `'not_identifiable_from_satellite_data'}` | {'class': 'Observation result', 'name': 'VA NOT IDENTIFIABLE FM STLT DATA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: VA NOT IDENTIFIABLE FM STLT DATA |
| `cand-16c8dc0874495318` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T19:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-20df0c4770a4dc72` | `S1_llm_only` | `'no_ash_expected_at_forecast_time'}` | {'class': 'Forecast time', 'name': '19/1200Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 19/1200Z NO VA EXP |
| `cand-3873befd0a489fab` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-53f8cfb949650db6` | `S1_llm_only` | `'located_in_area'}` | {'class': 'Geographic Area', 'name': 'MEXICO'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: MEXICO |
| `cand-62183d6e0fb0bcd4` | `S1_llm_only` | `'identifies_volcano'}` | {'class': 'Volcano', 'name': 'POPOCATEPETL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-6ce23877abf8d8f2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T06:06:00Z | `fact-b1626a69866c45d8` | `fact-b1626a69866c45d8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 06:09 |
| `cand-77471b3a8ee27dde` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T06:09:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 06:09 |
| `cand-89f6a94bb620ddcf` | `S1_llm_only` | `'reports_steam_gas_only_currently'}` | {'class': 'Emission type', 'name': 'STEAM/GAS EMS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WEBCAM SHOWS ONLY STEAM/GAS EMS CURRENTLY. |
| `cand-9d389c713999340b` | `S1_llm_only` | `'reported_source_elevation'}` | {'class': 'Elevation', 'name': '17693 FT AMSL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 17693 FT AMSL |
| `cand-a28f8fe057d6dea8` | `S1_llm_only` | `'warns_new_ash_emission_possible_any_time'}` | {'class': 'Probability statement', 'name': 'NEW VA EMS LIKELY AT ANY TIME'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW VA EMS LIKELY AT ANY TIME. |
| `cand-a328b5c1d0380afb` | `S1_llm_only` | `'ended_at_observation_time'}` | {'class': 'Observation Time', 'name': '19/0551Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS ENDED OBS VA DTG: 19/0551Z |
| `cand-bc821fe6580fee6e` | `S2_llm_schema_slice` | `advisoryNumber` | 13 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `cand-c6c154046040b81a` | `S1_llm_only` | `'indicates_not_detected_on_satellite_products'}` | {'class': 'Observation summary', 'name': 'VA NOT DETECTED ON VARIOUS STLT PRODUCTS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: VA NOT DETECTED ON VARIOUS STLT PRODUCTS. |
| `cand-d28a03dd5916288d` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190000-190000 |
| `cand-db13defb0c82d7f1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `fact-8a3474de6dad98e1` | `fact-8a3474de6dad98e1` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-f84d3921e54211fe` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `fact-f4f2e2273cc1a634` | `fact-f4f2e2273cc1a634` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |

## ATCSCC-GOLD-066 / 2026-05-17:011

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=41, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 20
- Cross-system clusters: 20
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=11

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 170910 WSI DDS:170912 VA ADVISORY DTG: 20260517/0910Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0004 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/486 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. GEOPHYSICAL INST. ERUPTION DETAILS: PSBL VA EMS. EST VA DTG: 17/0830Z EST VA CLD: SFC/FL150 S0000 W07751 - S0004 W07739 - S0005 W07740 - S0004 W07752 - S0000 W07751 MOV W 10KT FCST VA CLD +6HR: 17/1430Z SFC/FL150 N0001 W07753 - S0004 W07739 - S0005 W07740 - S0003 W07755 - N0001 W07753 FCST VA CLD +12HR: 17/2030Z SFC/FL150 N0003 W07752 - S0004 W07739 - S0005 W07739 - S0001 W07755 - N0003 W07752 FCST...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0fa777bd22b3f646` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-17T17:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-066:fact-03-d4d778714ac7` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-2722862003169d87` | `S1_llm_only` | `'reporting_action'}` | {'label': 'incr in seismic act near summit', 'type': 'activity_report'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | HWVR GEOPHYS INST RPRTD INCR IN SEISMIC ACT NEAR SUMMIT |
| `cand-286284c99ce66762` | `S1_llm_only` | `'time_reference'}` | {'label': '17/0830Z', 'type': 'datetime_utc'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 17/0830Z |
| `cand-31fdf55ce2c258bc` | `S1_llm_only` | `'forecast_prediction'}` | {'label': 'VA MOVG WNW', 'type': 'ash_movement'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NWP MDLS SUG ANY VA MOVG WNW |
| `cand-3707716e290b24d4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T00:00:00Z | `fact-7b8d71ea7714380d` | `fact-7b8d71ea7714380d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-4190533cd99f011f` | `S1_llm_only` | `'attribute'}` | {'label': '11686 FT AMSL', 'type': 'elevation'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-43b85fc2104d1ca9` | `S1_llm_only` | `'inference'}` | {'label': 'volc act', 'type': 'volcanic_activity'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPLYING VOLC ACT. |
| `cand-48034da8ade7dd43` | `S1_llm_only` | `'altitude_extent'}` | {'label': 'SFC/FL150', 'type': 'flight_level_range'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 |
| `cand-4a413d1d0becaf12` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-17T09:12:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-066:fact-04-6063f24bf0ef` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 09:12 |
| `cand-518912306bd70276` | `S1_llm_only` | `'activity_status'}` | {'label': 'PSBL VA EMS', 'type': 'event_description'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: PSBL VA EMS. |
| `cand-6291c14e2f19fbc0` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 11 | `fact-b5957d0c76b8fa62` | `S1b_llm_canonicalized:2026-05-17:011:fact-fcb5825df347, S2_llm_schema_slice:ATCSCC-GOLD-066:fact-01-8aa6e67a5928, fact-b5957d0c76b8fa62` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-8c78913c2a38f2c1` | `S1_llm_only` | `'movement_description'}` | {'label': '10KT', 'type': 'speed'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV W 10KT |
| `cand-9bfed303b910e283` | `S1_llm_only` | `'location_relation'}` | {'label': 'Ecuador', 'type': 'country'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-c0b5d7152edf88bd` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - REVENTADOR | `` | `S2_llm_schema_slice:ATCSCC-GOLD-066:fact-05-5628dcd5bd4e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-c460acb566838886` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T09:10:00Z | `fact-974e418e78f05a84` | `fact-974e418e78f05a84` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 09:12 |
| `cand-c5f1e5edcecd4745` | `S1_llm_only` | `'forecast_prediction'}` | {'label': 'LTLCG', 'type': 'change_assessment'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | WITH LTLCG FCST BY NWP MDLS. |
| `cand-cd8da35fd8cfdc55` | `S1_llm_only` | `'observation_limitation'}` | {'label': 'volcanic ash not observed', 'type': 'observation_result'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO WX CLD CVR VA NOT OBSD BY EITHER WEBCAM OR STLT. |
| `cand-dd069a687c6d3546` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `fact-f6fdeb3fd146fcb2` | `fact-f6fdeb3fd146fcb2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |
| `cand-e7f31ee05ffb5f19` | `S1_llm_only` | `'describes_subject'}` | {'label': 'Reventador', 'type': 'volcano'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-f02bc74c55b2cd8b` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-17T17:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-066:fact-02-563772c10a18` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170000-170000 |

## ATCSCC-GOLD-069 / 2026-05-20:192

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=41, est=13 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 20
- Cross-system clusters: 20
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=192

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 192 PHL/ZNY 05/20/2026 CDM GS CNX MESSAGE: CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1a7758f9835de490` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 192 | `fact-a9b10253ca03f333` | `fact-a9b10253ca03f333` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 192 PHL/ZNY 05/20/2026 CDM GS CNX |
| `cand-1ada831ea280a15a` | `S1_llm_only` | `has_controlled_element` | PHL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-35472c9210cc4174` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | nas:Airport/PHL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-4ad6c48300bf8761` | `S1_llm_only` | `was_signed_at` | 26/05/20 23:47 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 23:47 |
| `cand-6a363a3cc5a0deb7` | `S1_llm_only` | `has_applicability_period` | 20/2345Z - 21/0145Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 20/2345Z - 21/0145Z |
| `cand-7720fed320a23a15` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-2870341fecb819ba` | `fact-2870341fecb819ba` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 202347-210245 SIGNATURE: 26/05/20 23:47 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-7ad7af837b4ca1a0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T23:47:00Z | `fact-f8312c765227927a` | `fact-f8312c765227927a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 23:47 |
| `cand-7c0a88f2de4f40af` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-84f361cfd3b38173` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PHL | `fact-7edcb40f880f1121` | `fact-7edcb40f880f1121` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL |
| `cand-91c568411f2a0b79` | `S1_llm_only` | `announces_ground_stop_cancellation` | GS CNX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-9dc0e60563e106b9` | `S2_llm_schema_slice` | `initiativeComments` | GS CNX | `` | `S2_llm_schema_slice:ATCSCC-GOLD-069:fact-04-aff6d85eaa5a` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-a479aed928cd4a52` | `S2_llm_schema_slice` | `controlledNASelement` | PHL | `` | `S2_llm_schema_slice:ATCSCC-GOLD-069:fact-01-c0065032b345` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-a6180949579f4769` | `S1_llm_only` | `has_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-a772c155996d6a40` | `S1_llm_only` | `has_advisory_time` | 2345Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2345Z |
| `cand-ad37ee9e206e506f` | `S1_llm_only` | `references_air_traffic_control_system_command_center` | ATCSCC Advisory | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC Advisory |
| `cand-afb28de6788ff6de` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T23:47:00Z | `fact-d1b0c68f2347b3ab` | `fact-d1b0c68f2347b3ab` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202347-210245 |
| `cand-dca57f31d989aeb4` | `S1_llm_only` | `has_effective_time_range` | 202347-210245 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202347-210245 |
| `cand-de35591f1fed10d7` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T23:45:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-069:fact-02-fdc85ff81e4b` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |
| `cand-deec7d63dba45a99` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-21T02:45:00Z | `fact-d43eb01517276570` | `fact-d43eb01517276570` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202347-210245 |
| `cand-ff01592b21bedb8f` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-21T01:45:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-069:fact-03-0d252c9fe32c` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2345Z GS CNX PERIOD: 20/2345Z - 21/0145Z COMMENTS: EFFECTIVE TIME: 202347-210245 |

## ATCSCC-GOLD-094 / 2026-05-20:068

- Batch: `batch_10`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_10.md`
- Priority lane: `3_standard_review`
- Complexity: `medium` (score=41, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 20
- Cross-system clusters: 20
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=68

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH MESSAGE: FVAK21 PAWU 201504 WSI DDS:201506 VA ADVISORY DTG: 20260520/1504Z VAAC: ANCHORAGE VOLCANO: SHEVELUCH 300270 PSN: N5638 E16122 AREA: KAMCHATKA SOURCE ELEV: 10771 FT AMSL ADVISORY NR: 2026/112 INFO SOURCE: TOKYO VAAC. ERUPTION DETAILS: NOT PROVIDED OBS VA DTG: NOT PROVIDED OBS VA CLD: NOT PROVIDED FCST VA CLD +6HR: 20/2100Z NOT PROVIDED FCST VA CLD +12HR: 21/0300Z NOT PROVIDED FCST VA CLD +18HR: 21/0900Z NOT PROVIDED RMK: PLEASE SEE FVFE01 RJTD 201500 ISSUED BY TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. ...EVANS EFFECTIVE TIME: 200000-200000 SIGNATURE: 26/05/20 15:06 FAA.gov Home \| Privac...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-15318c9b9a504aca` | `S1_llm_only` | `reported information source` | Tokyo VAAC | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INFO SOURCE: TOKYO VAAC. |
| `cand-190b19793af9468b` | `S1_llm_only` | `has position` | N5638 E16122 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5638 E16122 |
| `cand-20e105646d021bc7` | `S1_llm_only` | `contains remark` | Please see FVFE01 RJTD 201500 issued by Tokyo VAAC that describes conditions near the Anchorage VAAC area of responsibility. | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | RMK: PLEASE SEE FVFE01 RJTD 201500 ISSUED BY TOKYO VAAC THAT DESCRIBES CONDITIONS NEAR THE ANCHORAGE VAAC AREA OF RESPONSIBILITY. |
| `cand-53c63f7159dba7ad` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:00:00Z | `fact-ebd018d05c535abb` | `fact-ebd018d05c535abb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-572766eaeff51308` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `fact-45530e2486bb3736` | `fact-45530e2486bb3736` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200000-200000 |
| `cand-59338804e2e00222` | `S1_llm_only` | `eruption details status` | not provided | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: NOT PROVIDED |
| `cand-6a9b01b2d1d3856a` | `S1_llm_only` | `observed volcanic ash date time status` | not provided | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA DTG: NOT PROVIDED |
| `cand-7e128763c442d189` | `S1_llm_only` | `has location area` | Kamchatka | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA |
| `cand-82fc59eb02b85ef6` | `S1_llm_only` | `forecast volcanic ash cloud +12hr status` | not provided | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 21/0300Z NOT PROVIDED |
| `cand-a6b207d6e648444f` | `S2_llm_schema_slice` | `unmapped_payload` |  | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1, "unknown_fact_type": 1, "unknown_predicate": 1}` |  |
| `cand-a7dd2c39be36ab18` | `S1_llm_only` | `forecast volcanic ash cloud +18hr status` | not provided | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 21/0900Z NOT PROVIDED |
| `cand-ace88d91890ab3ed` | `S1_llm_only` | `reported by advisory center` | Anchorage VAAC | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: ANCHORAGE |
| `cand-b6afdd48dd5cd94f` | `S1_llm_only` | `forecast volcanic ash cloud +6hr status` | not provided | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 20/2100Z NOT PROVIDED |
| `cand-ba72f8e2a4350948` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T15:04:00Z | `fact-9cca64e72d1554c3` | `fact-9cca64e72d1554c3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 15:06 |
| `cand-c7048fafc0c77182` | `S1_llm_only` | `effective time` | 200000-200000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200000-200000 |
| `cand-c73311ac85f29286` | `S1_llm_only` | `names volcano` | Sheveluch | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-d165865962748178` | `S1_llm_only` | `has source elevation` | 10771 FT AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 10771 FT AMSL |
| `cand-e824d7ef6ef0b1b3` | `S1_llm_only` | `has advisory type` | Volcanic Activity Bulletin | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-f3fad562be61cf28` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 68 | `fact-19c0c1de3408a16c` | `S1b_llm_canonicalized:2026-05-20:068:fact-0d0e11efb33b, fact-19c0c1de3408a16c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `cand-fe0da22d36423d99` | `S1_llm_only` | `observed volcanic ash cloud status` | not provided | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OBS VA CLD: NOT PROVIDED |

## ATCSCC-GOLD-033 / 2026-05-18:025

- Batch: `batch_04`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_04.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=39, est=13 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 19
- Cross-system clusters: 19
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=25

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX MESSAGE: CTL ELEMENT: LAS ELEMENT TYPE: APT ADL TIME: 0750Z GDP CNX PERIOD: 18/0750Z - 18/1854Z DISREGARD EDCTS FOR DEST LAS COMMENTS: EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05f87111c8268a3e` | `S2_llm_schema_slice` | `controlledNASelement` | nas:LAS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS ELEMENT TYPE: APT |
| `cand-1287b7646d856ce9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T07:50:00Z | `fact-0fa99c706b78e828` | `fact-0fa99c706b78e828` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180750-181954 |
| `cand-39355363e63c8c5a` | `S1_llm_only` | `'GDP CNX'}` | {'label': 'ground delay program cancellation', 'value': 'GDP CNX'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-419e20266cb43fe1` | `S2_llm_schema_slice` | `initiativeComments` | DISREGARD EDCTS FOR DEST LAS | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: EFFECTIVE TIME: 180750-181954 |
| `cand-4a1f599192a9f9b8` | `S1_llm_only` | `'DISREGARD'}` | {'label': 'EDCTS for destination LAS', 'value': 'EDCTS FOR DEST LAS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DISREGARD EDCTS FOR DEST LAS |
| `cand-4f6ea6bcb991dc93` | `S1_llm_only` | `'GDP CNX PERIOD'}` | {'label': '18/0750Z - 18/1854Z', 'value': '18/0750Z - 18/1854Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GDP CNX PERIOD: 18/0750Z - 18/1854Z |
| `cand-544bfa3ab381e86b` | `S1_llm_only` | `'ADL TIME'}` | {'label': '0750Z', 'value': '0750Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 0750Z |
| `cand-5595163c7baa76f1` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | LAS | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-5bccad478205a0ab` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 25 | `fact-e01a6e0c6659405a` | `S1b_llm_canonicalized:2026-05-18:025:fact-0703ee9d6045, fact-e01a6e0c6659405a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-776f23fba42681e5` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T19:54:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-8174e1a17e317f2e` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T07:50:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-851b995f0e0ad673` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T07:50:00Z | `fact-a6231c4c86e9ca39` | `fact-a6231c4c86e9ca39` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 07:50 |
| `cand-884241e4302debb0` | `S2_llm_schema_slice` | `advisoryNumber` | 25 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `cand-8ff4615cf5c01a54` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T19:54:00Z | `fact-7e694629ee98a3d5` | `fact-7e694629ee98a3d5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180750-181954 |
| `cand-934208a4f24bd1ec` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `fact-b2bc83d932302aa9` | `S1b_llm_canonicalized:2026-05-18:025:fact-f5a615ba9608, fact-b2bc83d932302aa9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: LAS |
| `cand-b2ffac2c71a6a27e` | `S1_llm_only` | `'CTL ELEMENT'}` | {'label': 'LAS', 'value': 'LAS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: LAS |
| `cand-e9008eccc798d66a` | `S1_llm_only` | `'EFFECTIVE TIME'}` | {'label': '180750-181954', 'value': '180750-181954'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180750-181954 |
| `cand-f425d44c55b948ff` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-5eb25f3e5c69a127` | `fact-5eb25f3e5c69a127` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 180750-181954 SIGNATURE: 26/05/18 07:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-f8d8bc998262f46d` | `S1_llm_only` | `'ELEMENT TYPE'}` | {'label': 'APT ADL', 'value': 'APT ADL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |

## ATCSCC-GOLD-043 / 2026-05-19:008

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=39, est=13 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 19
- Cross-system clusters: 19
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=8

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 190302-191230 SIGNATURE: 26/05/19 03:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-23706449ac1fe50a` | `S1_llm_only` | `'shows_effective_time_as'}` | {'label': '190302-191230', 'type': 'effective_time_string'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190302-191230 |
| `cand-265edd8e487f21d8` | `S1_llm_only` | `'announces_closed_status_of'}` | {'label': 'En Route TCA/Hotline web page', 'type': 'web_page'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. |
| `cand-300f17961807e6f6` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-19T03:02:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-043:fact-02-a84ce16911b9` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:02 |
| `cand-3a9d350c079bc73c` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-043:fact-05-362905714b44` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| `cand-4407f5878b82ef94` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T03:00:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-043:fact-03-10c3f543c033` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE... |
| `cand-52545e96d1e08501` | `S1_llm_only` | `'instructs_use_of'}` | {'label': 'normal ATCSCC phone lines', 'type': 'phone_lines'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-59cdcaf48011f245` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T12:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-043:fact-04-5431951b0125` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE... |
| `cand-734b48c0bed1f4e9` | `S2_llm_schema_slice` | `initiativeComments` | EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSIS... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-043:fact-05-40241c5df096` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE... |
| `cand-7ba39ef03c0204b1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 8 | `fact-f13facea2f62eb52` | `fact-f13facea2f62eb52` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| `cand-817ca64004d62151` | `S2_llm_schema_slice` | `advisoryNumber` | 8 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-043:fact-01-0b761bd06599` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE... |
| `cand-8367d05047ac5fb5` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-19T03:02:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-043:fact-03-ccd9c2be7cb7` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-aeb02f27ae9d6ac6` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-043:fact-06-75e975f93985` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-b5faf793471d1066` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 8 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-043:fact-01-29ba698691ba` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 |
| `cand-bc174b0c0114647e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T12:30:00Z | `fact-5c1dfd5984f99bef` | `fact-5c1dfd5984f99bef` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-c0487bc97d47b3ce` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T03:02:00Z | `fact-3a0a0f01866f899f` | `fact-3a0a0f01866f899f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-c3502b79432ae522` | `S1_llm_only` | `'effective_during'}` | {'label': '19/0300 - 19/1230', 'type': 'time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/0300 - 19/1230 |
| `cand-c70813cd7fd7957e` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-19T12:30:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-043:fact-04-70aeeae02ef1` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190302-191230 |
| `cand-ccc2d727f07aa495` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T03:02:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-043:fact-02-33d5803b885e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION MESSAGE: EVENT TIME: 19/0300 - 19/1230 THE EN ROUTE TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE... |
| `cand-da01d533fb6a4771` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T03:02:00Z | `fact-3f5091e0fb736c46` | `fact-3f5091e0fb736c46` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:02 |

## ATCSCC-GOLD-047 / 2026-05-14:033

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=39, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 19
- Cross-system clusters: 19
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=33

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE MESSAGE: FVXX24 KNES 141100 WSI DDS:141102 VA ADVISORY DTG: 20260514/1100Z VAAC: WASHINGTON VOLCANO: PURACE 351060 PSN: N0219 W07624 AREA: COLOMBIA SOURCE ELEV: 15256 FT AMSL ADVISORY NR: 2026/071 INFO SOURCE: GOES-19. VONA. NWP MODELS. ERUPTION DETAILS: VA EM DETECTED EST VA DTG: 14/1030Z EST VA CLD: SFC/FL170 N0232 W07632 - N0220 W07623 - N0217 W07624 - N0225 W07640 - N0232 W07632 MOV NW 5KT FCST VA CLD +6HR: 14/1630Z SFC/FL170 N0241 W07637 - N0220 W07623 - N0217 W07624 - N0230 W07648 - N0241 W07637 FCST VA CLD +12HR: 14/2230Z SFC/FL170 N0238 W07641 - N0220 W07623 - N0217 W07624 - N0225 W07650 - N0238 W07641 FCST VA CLD +18HR: 15/0430Z S...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b0c080c737e786b` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 33 | `fact-6d2bcb2243d90214` | `S1b_llm_canonicalized:2026-05-14:033:fact-f7a7fadcfce0, fact-6d2bcb2243d90214` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-2f56d41a1e0c90e8` | `S1_llm_only` | `'has_position'}` | {'label': 'N0219 W07624', 'type': 'coordinates'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: PURACE 351060 PSN: N0219 W07624 |
| `cand-3b80494d541413f6` | `S1_llm_only` | `'was_not_seen_in'}` | {'label': 'satellite image', 'type': 'imagery'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT SEEN IN STLT IMG DUE TO MET CLD CVR IN SUMMIT AREA. |
| `cand-3da92497c88e24c6` | `S1_llm_only` | `'reports_ash_emission_moving_from'}` | {'label': 'summit', 'type': 'location'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VONA RCVD FOR VA EM MOVNG NW FM SUMMIT. |
| `cand-4c8635e6d5a0381e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `fact-eb033d9b93c3e236` | `fact-eb033d9b93c3e236` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-5b3201ba096aa883` | `S1_llm_only` | `'is_moving'}` | {'label': 'NW 5KT', 'type': 'movement'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 5KT |
| `cand-916b5d1bf8be0f23` | `S1_llm_only` | `'forecast_position_at_plus_12_hours'}` | {'label': 'N0238 W07641', 'type': 'coordinates'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/2230Z SFC/FL170 N0238 W07641 - N0220 W07623 - N0217 W07624 - N0225 W07650 - N0238 W07641 |
| `cand-98b134aae249d283` | `S1_llm_only` | `'is_in_area'}` | {'label': 'Colombia', 'type': 'country'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: COLOMBIA |
| `cand-a0cd9745a7cbd019` | `S1b_llm_canonicalized` | `advisoryNumber` | 33 | `` | `S1b_llm_canonicalized:2026-05-14:033:fact-b6bbd3accf0b` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/071 |
| `cand-a7dcec86c28fd123` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `fact-dbbf80e28897542c` | `fact-dbbf80e28897542c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-b1fa442bdccc50c1` | `S1_llm_only` | `'forecast_position_at_plus_18_hours'}` | {'label': 'N0232 W07646', 'type': 'coordinates'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 15/0430Z SFC/FL170 N0232 W07646 - N0220 W07623 - N0217 W07623 - N0217 W07651 - N0232 W07646 |
| `cand-b82c58ef708eaaa2` | `S1_llm_only` | `'forecast_position_at_plus_6_hours'}` | {'label': 'N0241 W07637', 'type': 'coordinates'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/1630Z SFC/FL170 N0241 W07637 - N0220 W07623 - N0217 W07624 - N0230 W07648 - N0241 W07637 |
| `cand-c242b9ea21c50432` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T11:00:00Z | `fact-96d769cbd7a34389` | `fact-96d769cbd7a34389` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 11:02 |
| `cand-c2be2857c37a72a6` | `S1_llm_only` | `'reports_advisory_number'}` | {'label': '2026/071', 'type': 'advisory_number'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/071 |
| `cand-d2f257c54c466e57` | `S1_llm_only` | `'expected_movement_through'}` | {'label': 'T+18 HRS', 'type': 'time_span'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EXP WNW MOVNT THRU T+18 HRS. |
| `cand-e3e6c1586bceb23e` | `S1_llm_only` | `'identifies_volcano'}` | {'label': 'Purace', 'type': 'volcano'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `cand-e4cb4d9ad54ee7ce` | `S1_llm_only` | `'has_observed_vertical_extent'}` | {'label': 'SFC/FL170', 'type': 'flight_level_range'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL170 |
| `cand-eb310468619726f5` | `S1_llm_only` | `'was_detected_at'}` | {'label': '14/1030Z', 'type': 'time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: VA EM DETECTED EST VA DTG: 14/1030Z |
| `cand-f2e163f78efa3fbe` | `S1_llm_only` | `'has_source_elevation'}` | {'label': '15256 FT AMSL', 'type': 'elevation'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 15256 FT AMSL |

## ATCSCC-GOLD-070 / 2026-05-14:014

- Batch: `batch_07`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_07.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=39, est=14 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 19
- Cross-system clusters: 19
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=14

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO MESSAGE: FVXX20 KNES 140155 WSI DDS:140157 VA ADVISORY DTG: 20260514/0155Z VAAC: WASHINGTON VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA SOURCE ELEV: 12346 FT AMSL ADVISORY NR: 2026/559 INFO SOURCE: GOES-19. WEBCAM. NWP MODELS. ERUPTION DETAILS: LIKELY VA EMS EST VA DTG: 14/0130Z EST VA CLD: SFC/FL150 N1429 W09101 - N1429 W09052 - N1428 W09052 - N1421 W09058 - N1429 W09101 MOV SW 10KT FCST VA CLD +6HR: 14/0730Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1411 W09055 - N1416 W09104 - N1429 W09053 FCST VA CLD +12HR: 14/1330Z SFC/FL150 N1429 W09052 - N1428 W09052 - N1415 W09100 - N1421 W09106 - N1429 W09052 FCST VA CLD +18HR: 14/1930Z...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0f021019706807ae` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - FUEGO | `` | `S2_llm_schema_slice:ATCSCC-GOLD-070:fact-03-1f0dee8c038f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-0fcb9fa336229a04` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 14 | `fact-fabcfa32914abcd5` | `S1b_llm_canonicalized:2026-05-14:014:fact-0845f9a75460, S2_llm_schema_slice:ATCSCC-GOLD-070:fact-01-688d2ff40d5c, fact-fabcfa32914abcd5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-1c1ad3921bd6942e` | `S1_llm_only` | `'were not observed on satellite or webcam due to weather clouds'}` | {'label': 'weather clouds', 'type': 'weather_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS NOT OBS ON STLT OR WEBCAM DUE TO WX CLDS |
| `cand-2fc49771b69de671` | `S1_llm_only` | `'source elevation is'}` | {'label': '12346 FT AMSL', 'type': 'elevation'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 12346 FT AMSL |
| `cand-327ffda00881fd72` | `S1_llm_only` | `'has bulletin subject'}` | {'label': 'Fuego volcanic activity bulletin', 'type': 'bulletin'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `cand-6bc02ef3115709d1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T01:55:00Z | `fact-7f608b06ee5eaa4f` | `fact-7f608b06ee5eaa4f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 01:57 |
| `cand-7467cef155e37bd8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-14T00:00:00Z | `fact-87ac1834a53b7fa9` | `fact-87ac1834a53b7fa9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-861692578054d72d` | `S1_llm_only` | `'forecast position time plus 18 hours is'}` | {'label': '14/1930Z', 'type': 'time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +18HR: 14/1930Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1415 W09058 - N1420 W09104 - N1429 W09053 |
| `cand-8a4b4125cdbff34c` | `S1_llm_only` | `'eruption activity is assessed as'}` | {'label': 'likely volcanic ash emissions', 'type': 'eruption_assessment'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: LIKELY VA EMS |
| `cand-8d3dca3fc5b9c1ef` | `S1_llm_only` | `'forecast position time plus 6 hours is'}` | {'label': '14/0730Z', 'type': 'time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +6HR: 14/0730Z SFC/FL150 N1429 W09053 - N1428 W09052 - N1411 W09055 - N1416 W09104 - N1429 W09053 |
| `cand-99b15c7755d1d509` | `S1_llm_only` | `'continue'}` | {'label': 'continue', 'type': 'activity_state'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BUT EMS LIKELY TO CONT. |
| `cand-a70de516b528ae25` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T01:57:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-070:fact-02-2275746528a6` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 01:57 |
| `cand-aa3cc98cba681258` | `S1_llm_only` | `'is moving'}` | {'label': 'SW at 10KT', 'type': 'movement'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV SW 10KT |
| `cand-c377188a19b6d63a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T00:00:00Z | `fact-3b5bea061ec3d76c` | `fact-3b5bea061ec3d76c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140000-140000 |
| `cand-c3e7d2a804174d45` | `S1_llm_only` | `'estimated position time is'}` | {'label': '14/0130Z', 'type': 'time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA DTG: 14/0130Z |
| `cand-c54e315698aa97ba` | `S1_llm_only` | `'is expected through'}` | {'label': 'T+18', 'type': 'forecast_horizon'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GEN SW MVMT EXP THRU T+18 ACCORDING TO NWP MDLS |
| `cand-efedfc1aaccb0c00` | `S1_llm_only` | `'estimated vertical extent is'}` | {'label': 'SFC/FL150', 'type': 'altitude_range'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL150 N1429 W09101 - N1429 W09052 - N1428 W09052 - N1421 W09058 - N1429 W09101 |
| `cand-f96dcdab8e2b50dd` | `S1_llm_only` | `'is located in'}` | {'label': 'Guatemala', 'type': 'country_or_region'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VOLCANO: FUEGO 342090 PSN: N1428 W09052 AREA: GUATEMALA |
| `cand-fb9773855c2f715c` | `S1_llm_only` | `'forecast position time plus 12 hours is'}` | {'label': '14/1330Z', 'type': 'time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCST VA CLD +12HR: 14/1330Z SFC/FL150 N1429 W09052 - N1428 W09052 - N1415 W09100 - N1421 W09106 - N1429 W09052 |

## ATCSCC-GOLD-080 / 2026-05-18:148

- Batch: `batch_08`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_08.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=39, est=13 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 19
- Cross-system clusters: 19
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=148

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-06f38ba189886a45` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T22:41:00Z | `fact-1c8975f4096b451e` | `fact-1c8975f4096b451e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182241-190150 |
| `cand-0a0f3532b8487b1d` | `S1_llm_only` | `'time_interval'}` | {'label': '182241-190150', 'type': 'effective_time_range'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182241-190150 |
| `cand-10e22368ce990b27` | `S1_llm_only` | `'headline'}` | {'label': 'ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX', 'type': 'advisory_headline'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX |
| `cand-17cf13381378c5c3` | `S2_llm_schema_slice` | `controlledNASelement` | {'label': 'BNA', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
| `cand-39268567ca4cc380` | `S1_llm_only` | `'element_type'}` | {'label': 'APT ADL', 'type': 'element_type_value'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-49c2bbccc9d8e59a` | `S1_llm_only` | `'time_interval'}` | {'label': '18/2236Z - 19/0050Z', 'type': 'time_period'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PERIOD: 18/2236Z - 19/0050Z |
| `cand-4aa4ffa209c53d30` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T22:41:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 22:41 |
| `cand-4ead146520b970a3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-56358f2963896fba` | `fact-56358f2963896fba` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182241-190150 SIGNATURE: 26/05/18 22:41 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-648b05addaf018ec` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `fact-8b6307238e8cd386` | `S1b_llm_canonicalized:2026-05-18:148:fact-89c012fad318, fact-8b6307238e8cd386` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: BNA |
| `cand-67ca64df3bc1d7b0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T01:50:00Z | `fact-cca43a9fdd809ad9` | `fact-cca43a9fdd809ad9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182241-190150 |
| `cand-726827abb533ab33` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T22:36:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |
| `cand-7352dc480ac48aa8` | `S1_llm_only` | `'time'}` | {'label': '2236Z', 'type': 'zulu_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2236Z |
| `cand-7d7af8cc3455b208` | `S1_llm_only` | `'control_element'}` | {'label': 'BNA', 'type': 'airport_element'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-8953923c9432763e` | `S2_llm_schema_slice` | `initiativeComments` | GS CNX | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: |
| `cand-aaf0ab19ace2164c` | `S1_llm_only` | `'status_change'}` | {'label': 'GS CNX', 'type': 'operation_status'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GS CNX |
| `cand-b8a3b529351002a4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T22:41:00Z | `fact-11f32ed5f7fd403f` | `fact-11f32ed5f7fd403f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 22:41 |
| `cand-d1370d2225594222` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 148 | `fact-d4d441604d99241b` | `S1b_llm_canonicalized:2026-05-18:148:fact-63fd2d998088, fact-d4d441604d99241b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX |
| `cand-e544f8aa1681e8df` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'label': 'BNA', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z COMMENTS: |
| `cand-ebeceab860d3527e` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T00:50:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2236Z GS CNX PERIOD: 18/2236Z - 19/0050Z |

## ATCSCC-GOLD-090 / 2026-05-15:061

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=39, est=13 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 19
- Cross-system clusters: 19
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=61

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 151849-152030 SIGNATURE: 26/05/15 18:49 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0703fc3843d29ecf` | `S2_llm_schema_slice` | `reRouteReason` | OTHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-07-4a0e7caf2ce6` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-12ff7c8e36f83676` | `S2_llm_schema_slice` | `reRouteType` | FCA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-06-626540748227` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-225b32cfd279489f` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-15T18:49:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-02-683de2229311` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-394a9427d3385086` | `S1_llm_only` | `has_effective_time` | 151849-152030 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151849-152030 |
| `cand-3b247360808b1922` | `S1_llm_only` | `has_status` | cancelled | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. |
| `cand-48a8209359defff1` | `S2_llm_schema_slice` | `initiativeComments` | FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-08-5711791c2815` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-4ded2e61eaaf84d8` | `S2_llm_schema_slice` | `controlledNASelement` | {"evidence_text": "FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS:", "type": "nas:A... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-09-83941dcb3701` | `{"repaired_accepted": 1}` | `{}` | FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: |
| `cand-5706831032f1e78f` | `S1_llm_only` | `message_type` | reroute cancellation | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION |
| `cand-6804f514149409cb` | `S1_llm_only` | `cancels_reference_advisory` | ADVZY 024 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: |
| `cand-6b1b80bd23a8554d` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 61 | `fact-1d7a66688db929ee` | `S1b_llm_canonicalized:2026-05-15:061:fact-eb456fb57eaa, fact-1d7a66688db929ee` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION |
| `cand-8794711dbce0e9b2` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-04-7043d37bb2d1` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-89a2ea6c2625f5f5` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-15T18:49:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-03-5e0ea3e21322` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-8dce73f0301551d6` | `S2_llm_schema_slice` | `advisoryNumber` | 61 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-01-f941ccf969e7` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-a4f275de0537c1bb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T18:49:00Z | `fact-813b57b39ad9e674` | `fact-813b57b39ad9e674` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 18:49 |
| `cand-b000cf7eca091ea4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T20:30:00Z | `fact-a42ad0f8f551e246` | `fact-a42ad0f8f551e246` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151849-152030 |
| `cand-c7c0e885c4098f37` | `S2_llm_schema_slice` | `implementationStatus` | FYI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-090:fact-05-8771827ca742` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-cc0de7da6c373558` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 61 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-090:fact-01-d52790b1819f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION MESSAGE: FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED. REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: EFFECTIVE TIM... |
| `cand-cdc623c8aed2bc19` | `S1b_llm_canonicalized` | `advisoryNumber` | 61 | `` | `S1b_llm_canonicalized:2026-05-15:061:fact-1128e94898e7` | `{"repaired_accepted": 1}` | `{}` | REMARKS: CANCELS ADVZY 024 ASSOCIATED RESTRICTIONS: |
| `cand-e9329b80d227d255` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T18:49:00Z | `fact-3fac184dd2dbbeae` | `fact-3fac184dd2dbbeae` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151849-152030 |

## ATCSCC-GOLD-099 / 2026-05-20:004

- Batch: `batch_10`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_10.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=39, est=13 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 19
- Cross-system clusters: 19
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=4

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 200016-200630 SIGNATURE: 26/05/20 00:16 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-26ad29a873d68c3f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T00:16:00Z | `fact-602dfbd54903f0ee` | `fact-602dfbd54903f0ee` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 00:16 |
| `cand-2ca5cf75b611e7d6` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 4 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-099:fact-01-8976e8a4116e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-2f1bb9bba9bc97f3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T06:30:00Z | `fact-c0316629fdddb8dc` | `fact-c0316629fdddb8dc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200016-200630 |
| `cand-399f74b82304536c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T00:16:00Z | `fact-bdf7c6815b08e5cd` | `fact-bdf7c6815b08e5cd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 200016-200630 |
| `cand-4abe9b6a1915a3be` | `S1_llm_only` | `is` | 200016-200630 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 200016-200630 |
| `cand-4b6d692f2a1024f8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 4 | `fact-0bf852005f1a08f3` | `fact-0bf852005f1a08f3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-4c2381e2c4e6a40f` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingConditionMessage` | EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERS... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-099:fact-06-640abde73383` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-4ca1145be59b411b` | `S1_llm_only` | `maximum_duration` | up to 30 minutes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-61b1b1310ba08eba` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-099:fact-05-a5756eeb91f4` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-64bed96bbd457385` | `S1_llm_only` | `caused_by` | thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-81b54c1b61b7478a` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | MEM Airport | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-099:fact-04-8aa6abfbca45` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-91170ebd290cc966` | `S1_llm_only` | `states_updates_will_follow_if_necessary` | updates will follow if necessary | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-93db1731e1e24c98` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-20T00:16:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-099:fact-02-e65eb628a4fe` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-b0465426ea06276c` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-20T06:30:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-099:fact-03-338f1792b6fe` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-bb94bc4fb26d6fb5` | `S1_llm_only` | `can_expect_arrival_delays_into` | MEM AIRPORT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-f607542441e32871` | `S1b_llm_canonicalized` | `impactingCondition` | thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-f8e246eb5f85fda7` | `S1_llm_only` | `can_expect_airborne_holding_into` | MEM AIRPORT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-fa9399d3400c14b6` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERS... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-099:fact-07-4f5aaa551f22` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `cand-fd63bd5f29f6e12d` | `S1_llm_only` | `announces_event_time_window` | 20/0030 - 20/0600 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 20/0030 - 20/0600 USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MEM AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |

## ATCSCC-GOLD-046 / 2026-05-18:040

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=35, est=12 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 17
- Cross-system clusters: 17
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=40

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY MESSAGE: FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA SOURCE ELEV: 9456 FT AMSL ADVISORY NR: 2026/006 EFFECTIVE TIME: 180000-180000 SIGNATURE: 26/05/18 12:08 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0b8c7952de0151e7` | `S1_llm_only` | `has_position` | N5559 E16035 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PSN: N5559 E16035 |
| `cand-37af7000f1f8116c` | `S2_llm_schema_slice` | `controlledNASelement` | BEZYMIANNY | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA |
| `cand-470197c39e38168f` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T12:08:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-046:fact-02-93508720f477` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 12:08 |
| `cand-4eddadf624bd3f4f` | `S1_llm_only` | `is_located_in_area` | KAMCHATKA PENINSULA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: KAMCHATKA PENINSULA |
| `cand-608762802b7c6601` | `S1_llm_only` | `has_advisory_number` | 2026/006 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADVISORY NR: 2026/006 |
| `cand-61b74d1d30bf3b09` | `S1_llm_only` | `reports_message_line` | FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 ARE... | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FVAK21 PAWU 181208 WSI DDS:181208 VAAAK1 VA ADVISORY DTG: 20260518/1200Z VAAC: ANCHORAGE VOLCANO: BEZYMIANNY 300250 PSN: N5559 E16035 AREA: KAMCHATKA PENINSULA SOURCE ELEV: 9456... |
| `cand-76f05d1536bb5e7a` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 40 | `fact-796d752dc583203a` | `S1b_llm_canonicalized:2026-05-18:040:fact-5b671196bc9b, S2_llm_schema_slice:ATCSCC-GOLD-046:fact-01-adfada51d091, fact-796d752dc583203a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-8cd64d90a7e0b0f5` | `S1b_llm_canonicalized` | `advisoryNumber` | 40 | `` | `S1b_llm_canonicalized:2026-05-18:040:fact-6aa75feddb61` | `{"repaired_accepted": 1}` | `{}` | ADVISORY NR: 2026/006 |
| `cand-9dfd3acf294a7fda` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T00:00:00Z | `fact-bc121483441965ab` | `fact-bc121483441965ab` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-a7dac989893edcd6` | `S1_llm_only` | `issues_volcano_advisory_for` | BEZYMIANNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VAAC: ANCHORAGE VOLCANO: BEZYMIANNY |
| `cand-ac9a1f2574cd8e96` | `S1_llm_only` | `has_signature_time` | 26/05/18 12:08 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 12:08 |
| `cand-b2e8266bc3c94c52` | `S1_llm_only` | `has_advisory_header` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `cand-c33d611130929f07` | `S1_llm_only` | `has_effective_time_window` | 180000-180000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180000-180000 |
| `cand-c834809086527b3f` | `S1_llm_only` | `has_source_elevation` | 9456 FT AMSL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 9456 FT AMSL |
| `cand-d32838e7ec233568` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T12:00:00Z | `fact-dbdcec0c6d5eb452` | `fact-dbdcec0c6d5eb452` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 12:08 |
| `cand-e9c12e516ea379c8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T00:00:00Z | `fact-da6cc775d557b40d` | `fact-da6cc775d557b40d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 180000-180000 |
| `cand-efc857af97803b48` | `S2_llm_schema_slice` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY | `` | `S2_llm_schema_slice:ATCSCC-GOLD-046:fact-03-6ca56766df9e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |

## ATCSCC-GOLD-085 / 2026-05-19:009

- Batch: `batch_09`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_09.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=35, est=13 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 17
- Cross-system clusters: 17
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=9

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR MESSAGE: FVXX25 KNES 190306 WSI DDS:190307 VA ADVISORY DTG: 20260519/0306Z VAAC: WASHINGTON VOLCANO: REVENTADOR 352010 PSN: S0004 W07739 AREA: ECUADOR SOURCE ELEV: 11686 FT AMSL ADVISORY NR: 2026/493 INFO SOURCE: GOES-19. NWP MODELS. ERUPTION DETAILS: ONGOING VA EMS EST VA DTG: 19/0250Z EST VA CLD: SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07740 - N0000 W07751 - N0004 W07748 MOV NW 15KT FCST VA CLD +6HR: 19/0900Z SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07740 - N0000 W07751 - N0004 W07748 FCST VA CLD +12HR: 19/1500Z SFC/FL140 N0004 W07748 - S0004 W07739 - S0005 W07739 - N0000 W07751 - N0004 W07748 FCST VA CLD +18HR: 19/2100Z...

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-1d14064bc6c09720` | `S1_llm_only` | `'has source area'}` | {'label': 'Ecuador', 'type': 'country'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AREA: ECUADOR |
| `cand-26e8d0d5940288ce` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 9 | `fact-7984ab03f70669d6` | `S1b_llm_canonicalized:2026-05-19:009:fact-18c0d2f9b537, S2_llm_schema_slice:ATCSCC-GOLD-085:fact-01-82cb0d64d49f, fact-7984ab03f70669d6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-2bca347bf460f031` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-19T03:07:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-085:fact-02-67ce62be9856, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-085:fact-03-67ce62be9856` | `{"repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/19 03:07 |
| `cand-32e21f75e105dad6` | `S1_llm_only` | `'has no change forecast for'}` | {'label': 'next 18 hours', 'type': 'time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NO CHG FCST TO MDL WINDS AT FL NXT 18 HR. |
| `cand-3728dd683a1bd243` | `S1_llm_only` | `'likely continue'}` | {'label': 'recent activity', 'type': 'activity'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA EMS LIKELY CONTINUE GIVEN RECENT ACTVTY. |
| `cand-39693846926ba1f2` | `S1_llm_only` | `'has source elevation'}` | {'label': '11686 ft AMSL', 'type': 'elevation'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOURCE ELEV: 11686 FT AMSL |
| `cand-50f434e6ad5e90d2` | `S1_llm_only` | `'moves northwest at'}` | {'label': '15 kt', 'type': 'speed'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MOV NW 15KT |
| `cand-8fc329eade16102e` | `S1_llm_only` | `'is observed from'}` | {'label': 'surface to flight level 140', 'type': 'vertical_extent'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EST VA CLD: SFC/FL140 |
| `cand-90962e52f41ddc70` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T03:06:00Z | `fact-f33e9cebb567454a` | `fact-f33e9cebb567454a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 03:07 |
| `cand-9db736f91d3d6579` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T00:00:00Z | `fact-e418a9981b48d903` | `S2_llm_schema_slice:ATCSCC-GOLD-085:fact-03-f3142770abbf, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-085:fact-04-f3142770abbf, fact-e418a9981b48d903` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-a0d2c106d37e230f` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-19T19:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-085:fact-05-f70d5463314d` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-afc9a12f8588e128` | `S1_llm_only` | `'is not detected due to'}` | {'label': 'weather clouds in summit area', 'type': 'weather_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VA NOT DETECTED ON STLT DUE TO WX CLDS IN SUMMIT AREA. |
| `cand-c7f7211b37c4263f` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `fact-7d24998b79e03fe5` | `S2_llm_schema_slice:ATCSCC-GOLD-085:fact-04-95dfa77ae03f, fact-7d24998b79e03fe5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 190000-190000 |
| `cand-ee2a7bfbb43f43ca` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | VOLCANIC ACTIVITY BULLETIN - REVENTADOR | `` | `S2_llm_schema_slice:ATCSCC-GOLD-085:fact-05-24ad78f41ddd, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-085:fact-02-24ad78f41ddd` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `cand-efa7f75ac8283fa1` | `S1_llm_only` | `'reports eruption details'}` | {'label': 'ongoing volcanic ash emissions', 'type': 'eruption_state'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ERUPTION DETAILS: ONGOING VA EMS |
| `cand-f7400c7e86cdb4ff` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 9 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-085:fact-01-67ae49b0eed0` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 009 |
| `cand-ffd38ef41f1ed0e4` | `S1_llm_only` | `'names volcano'}` | {'label': 'Reventador', 'type': 'volcano'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |

## ATCSCC-GOLD-095 / 2026-05-19:047

- Batch: `batch_10`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_10.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=35, est=12 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 17
- Cross-system clusters: 17
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=47

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 191453-191800 SIGNATURE: 26/05/19 14:53 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0d0f0b3919bc13a8` | `S2_llm_schema_slice` | `reRouteType` | FCA | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-103dc703946f5146` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-1220edfed626dd97` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 47 | `fact-efda94514ac952f9` | `fact-efda94514ac952f9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-4497725adf6f0555` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T14:53:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:53 |
| `cand-48b769eb5f3bd730` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T18:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |
| `cand-4ad329a720562a5d` | `S1_llm_only` | `has_status_change` | has been cancelled | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. |
| `cand-4c67bc0c63e9be17` | `S1_llm_only` | `has_message` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-57e73df87759e13f` | `S2_llm_schema_slice` | `advisoryNumber` | 47 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-6795d233730878ea` | `S2_llm_schema_slice` | `initiativeComments` | FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: FCA001:FDRER_PARTIAL HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-8484a779672cae41` | `S2_llm_schema_slice` | `implementationStatus` | FYI | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-874823263ac57ffe` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T14:53:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |
| `cand-a39484ee27bd5128` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T14:53:00Z | `fact-c8afc5a06a98268b` | `fact-c8afc5a06a98268b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 14:53 |
| `cand-a3d03c44b63ecbff` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T14:53:00Z | `fact-5bd11e3e29aa0b7a` | `fact-5bd11e3e29aa0b7a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191453-191800 |
| `cand-acea76b0bfb13fc1` | `S2_llm_schema_slice` | `reRouteReason` | OTHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `cand-cd1e5bfc1cb2e387` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T18:00:00Z | `fact-e717237bc47d0030` | `fact-e717237bc47d0030` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191453-191800 |
| `cand-e8f53247193e3d01` | `S1_llm_only` | `was_signed_at` | 26/05/19 14:53 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 14:53 |
| `cand-f48e96cfb6d98726` | `S1_llm_only` | `has_effective_time` | 191453-191800 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191453-191800 |

## ATCSCC-GOLD-048 / 2026-05-17:003

- Batch: `batch_05`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_05.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=33, est=11 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 16
- Cross-system clusters: 16
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=3

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. EFFECTIVE TIME: 170043-171200 SIGNATURE: 26/05/17 00:43 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08138ecf1101f27b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 3 | `fact-e8fe95a583b44db2` | `fact-e8fe95a583b44db2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION |
| `cand-1d8cd86549ae6f4f` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-17T00:43:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-048:fact-02-17a922830947` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER... |
| `cand-20b466decc9436fd` | `S1_llm_only` | `'state'}` | {'label': 'closed', 'type': 'status'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. |
| `cand-217db584d98a952c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `fact-1d6fcf65f960dea8` | `fact-1d6fcf65f960dea8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170043-171200 |
| `cand-2c79096a71c90f05` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-048:fact-05-caeb411a4210` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER... |
| `cand-314d92c01c7d5641` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-36abb1ca8be75a12` | `S2_llm_schema_slice` | `initiativeComments` | THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-3764a46d20692fd9` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-3f7bf62e61052804` | `S1_llm_only` | `'instruction'}` | {'label': 'normal ATCSCC phone lines', 'type': 'contact method'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER ASSISTANCE. |
| `cand-50eaa031cd2ea326` | `S1_llm_only` | `'time interval'}` | {'label': '170043-171200', 'type': 'time interval'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 170043-171200 |
| `cand-6e1f1ffd0d3e29f2` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 3 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-048:fact-01-345f198eb1c3` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER... |
| `cand-6f22109771e33824` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `fact-2835d68338bbc70d` | `fact-2835d68338bbc70d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 170043-171200 |
| `cand-ab7a06497b76b3d1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T00:43:00Z | `fact-683870d0cd7e977f` | `fact-683870d0cd7e977f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 00:43 |
| `cand-d3630610b6ee889d` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-17T12:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-048:fact-04-387bfe77ffab` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER... |
| `cand-d3ab2bd1dd1c96d7` | `S2_llm_schema_slice` | `advisoryNumber` | 3 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION |
| `cand-ff46fc1ce4f832c7` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-17T00:43:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-048:fact-03-1e1cbe8039d5` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION MESSAGE: THE TERMINAL TCA/HOTLINE WEB PAGE IS NOW CLOSED. PLEASE UTILIZE NORMAL ATCSCC PHONE LINES FOR FURTHER... |

## ATCSCC-GOLD-040 / 2026-05-20:197

- Batch: `batch_04`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_04.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=31, est=11 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 15
- Cross-system clusters: 15
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=197

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION MESSAGE: ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 202359-210200 SIGNATURE: 26/05/20 23:59 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0151d7b5e8976bd1` | `S2_llm_schema_slice` | `controlledNASelement` | {'name': 'ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. |
| `cand-0916c4248b064e90` | `S1_llm_only` | `has_remark` | associated restrictions | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-12fca6001e102b93` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 197 | `fact-94608c8d108c6d90` | `S1b_llm_canonicalized:2026-05-20:197:fact-c031bdc03a54, fact-94608c8d108c6d90` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-218acd50f943af4d` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T23:59:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 23:59 |
| `cand-26002cb331bb77dd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-21T02:00:00Z | `fact-2fb41fe3e1c5b4f8` | `fact-2fb41fe3e1c5b4f8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202359-210200 |
| `cand-29df9dfd7d6d3015` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-2d953801a51fee79` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-36a00cee0e02cedd` | `S1_llm_only` | `advisory_message_type` | reroute cancellation | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-544d7203ee032079` | `S1_llm_only` | `cancellation_status` | cancelled | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW_NATS_ESCAPE_VIA_GOATR_MODIFIED HAS BEEN CANCELLED. |
| `cand-5f7265f39c9c1835` | `S2_llm_schema_slice` | `reRouteReason` | OTHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-76cf775e02890168` | `S2_llm_schema_slice` | `reRouteType` | INFORMATIONAL | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-8ddf61aa108b2d0b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T23:59:00Z | `fact-7f3d018007dc419e` | `fact-7f3d018007dc419e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 23:59 |
| `cand-95df21765497c626` | `S1_llm_only` | `has_effective_time` | 202359-210200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202359-210200 |
| `cand-a04d6f47a774c8e7` | `S2_llm_schema_slice` | `advisoryNumber` | 197 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `cand-ffda238e74aa07e9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T23:59:00Z | `fact-71ee75bc4ccdad66` | `fact-71ee75bc4ccdad66` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202359-210200 |

## ATCSCC-GOLD-097 / 2026-05-16:067

- Batch: `batch_10`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_10.md`
- Priority lane: `3_standard_review`
- Complexity: `light` (score=27, est=11 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 13
- Cross-system clusters: 13
- Rejected facts: 0
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=67

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION MESSAGE: DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: EFFECTIVE TIME: 162225-170000 SIGNATURE: 26/05/16 22:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-024443dcc4dad155` | `S2_llm_schema_slice` | `initiativeComments` | DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: | `` | `S2_llm_schema_slice:ATCSCC-GOLD-097:fact-03-03a70b2c0a52` | `{"repaired_accepted": 1}` | `{}` | DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-0e2fad3244bb7ffa` | `S1_llm_only` | `has_effective_time_window` | 162225-170000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 162225-170000 |
| `cand-15672c022942c78e` | `S1_llm_only` | `has_remarks` | associated restrictions | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: ASSOCIATED RESTRICTIONS: |
| `cand-2f26a7fde84a912e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-16T22:25:00Z | `fact-3bfb59142e59b493` | `fact-3bfb59142e59b493` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162225-170000 |
| `cand-57fc15b97eda7373` | `S1_llm_only` | `has_signature_timestamp` | 26/05/16 22:25 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 22:25 |
| `cand-6f5ab98cdd9ecded` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T00:00:00Z | `fact-2fd368170d853184` | `fact-2fd368170d853184` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 162225-170000 |
| `cand-723f732c408429a6` | `S1_llm_only` | `has_status` | cancelled | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEN_GCK_2_MODIFIED HAS BEEN CANCELLED. |
| `cand-a12fd7682e4ac5ee` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-097:fact-05-fcf0595268dc` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-a9a81a2f09362a97` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-16T22:25:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-097:fact-02-8da0a66930cf` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 22:25 |
| `cand-c1d2d5458b9f225c` | `S2_llm_schema_slice` | `implementationStatus` | FYI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-097:fact-04-786975c69595` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-c21a9636fbc6935c` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 67 | `fact-de3f2004b1199900` | `S1b_llm_canonicalized:2026-05-16:067:fact-7836ab05a985, S2_llm_schema_slice:ATCSCC-GOLD-097:fact-01-53628bc76a11, fact-de3f2004b1199900` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `cand-d04f78766450362b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-16T22:25:00Z | `fact-3ab6f697ac82e26e` | `fact-3ab6f697ac82e26e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 22:25 |
| `cand-d5aec2541328395e` | `S1_llm_only` | `has_message_topic` | reroute cancellation | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
