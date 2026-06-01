# NASA ATMONTO Gold Review Priority Packet: 1_rejection_adjudication

- Label: Rejected-fact adjudication first
- Records: 40
- Estimated review time: 941 minutes
- Candidate clusters: 1500
- Cross-system clusters: 1464
- Rejected facts: 48

## Packet Checklist

- [ ] Read the source excerpt and open the source URL when the excerpt is insufficient.
- [ ] Copy source-supported S0 IDs into `valid_candidate_fact_ids`.
- [ ] Copy source-supported schema-valid S1-S3 IDs into `valid_cross_system_fact_ids`.
- [ ] Add corrected or missing facts manually when no candidate is source-correct.
- [ ] Complete rejected-fact adjudications when present.

## ATCSCC-GOLD-024 / 2026-05-18:136

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=97, est=29 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 46
- Cross-system clusters: 44
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=136

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2129Z GROUND STOP PERIOD: 18/2130Z - 18/2245Z DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 901 / 75 / 39 PROBABILITY OF EXTENSION: LOW IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-546d313b8f16f1ca` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |
| `fact-c1b6afb7f5738a06` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09fd167dc50d6c64` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 136 | `fact-380b135465278af5` | `S1b_llm_canonicalized:2026-05-18:136:fact-624c23f116fb, fact-380b135465278af5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-138b9c677d8dfbfb` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T21:31:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-17dea59a08effe51` | `S2_llm_schema_slice` | `initiativeComments` | STAFFING / STAFFING COMMENTS: | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-1d7f82ec8c1f1ccb` | `S2_llm_schema_slice` | `controlledNASelement` | {'id': 'BNA', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT |
| `cand-1e6b560f1675feb5` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZKC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-2340afc035f433b2` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZNY'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-237c6417370d3960` | `S1_llm_only` | `'effective_during'}` | {'label': '182131-182345'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-245e3f9218188877` | `S1b_llm_canonicalized` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-26889e56b45891fd` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:APT | `` | `S1b_llm_canonicalized:2026-05-18:136:fact-213fb46531e3` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL |
| `cand-286b28b93ff85a94` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-33573443e4cd72a6` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZID'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-40d1bfb4d6d4760f` | `S2_llm_schema_slice` | `impactingCondition` | other | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-4ebcf573704c556b` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZME'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-5712d720d06c60fb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T21:31:00Z | `fact-ace2c626a48a40ec` | `fact-ace2c626a48a40ec` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182131-182345 |
| `cand-571fc9e87c4ce74c` | `S1_llm_only` | `'starts_at'}` | {'label': '18/2130Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-66ed24ffa12c811b` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-67e98c878dfbf3f3` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-696688b8e2ef844c` | `S1_llm_only` | `'has_control_element_type'}` | {'label': 'APT ADL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL |
| `cand-6f1563cf130a516a` | `S0_rule_only` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-c1b6afb7f5738a06` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-7d2dce4221ed2655` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-81d918a74dd2f70d` | `S1_llm_only` | `'ends_at'}` | {'label': '18/2245Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-82984cbf2bf25dab` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T23:45:00Z | `fact-fc7a41ea570fa9b6` | `fact-fc7a41ea570fa9b6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182131-182345 |
| `cand-8604f488b9fb2706` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZTL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-89b755fab41c7e7a` | `S1_llm_only` | `'references_air_traffic_facility'}` | {'label': 'ZME'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-8c470008cbd0ad6f` | `S1_llm_only` | `'has_new_delays'}` | {'label': '901 / 75 / 39'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 901 / 75 / 39 |
| `cand-8cb241de1c37c205` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `fact-22684e35378b2471` | `fact-22684e35378b2471` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-8dc309d1ef5f56d9` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-92413edf53cebf59` | `S1_llm_only` | `'has_previous_delays'}` | {'label': '0 / 0 / 0'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-93ddb38014461dcc` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADL | `` | `S1b_llm_canonicalized:2026-05-18:136:fact-fdb108896b1d` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL |
| `cand-9fe0138ebe8bf2df` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-a1943333063ec8bb` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-a815502d2cae7ab2` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZFW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-a8a086e51688bed5` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T22:45:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182131-182345 |
| `cand-aa3df19feb940e20` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `extensionProbability` | LOW | `fact-52888cfe9889b930` | `S1b_llm_canonicalized:2026-05-18:136:fact-9be76c6beca0, fact-52888cfe9889b930` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: LOW |
| `cand-aa42feb8d9c361f6` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-add7a13d3997fb37` | `S1_llm_only` | `'announces_ground_stop_for'}` | {'label': 'BNA'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `cand-aed512b3ad3e8647` | `S0_rule_only` | `impactingCondition` | staffing | `fact-546d313b8f16f1ca` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-c6029b6b4ae79d34` | `S1_llm_only` | `'has_probability_of_extension'}` | {'label': 'LOW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-d4faf6c27e3dbe69` | `S1_llm_only` | `'has_advisory_time'}` | {'label': '2129Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2129Z GROUND STOP PERIOD: 18/2130Z - 18/2245Z |
| `cand-df171d1156f63ddd` | `S1_llm_only` | `'has_impacting_condition'}` | {'label': 'STAFFING'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-df5e86e858e0a9f4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-d221b64a3aae9663` | `fact-d221b64a3aae9663` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182131-182345 SIGNATURE: 26/05/18 21:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-e1798b2806e8574b` | `S2_llm_schema_slice` | `extensionProbability` | LOW | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: LOW |
| `cand-e47958f2b535bf04` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZHU'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-e87d81e4d0da674c` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'ZAU'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZNY ZHU ZFW ZKC ZME ZID |
| `cand-ebe3d7c5dec976c5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T21:31:00Z | `fact-4a08bfe17902f89a` | `fact-4a08bfe17902f89a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 21:31 |
| `cand-fbd2fd14eb60cc79` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |

## ATCSCC-GOLD-023 / 2026-05-20:163

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=87, est=27 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 41
- Cross-system clusters: 39
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=163

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1918 / 74 / 46 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-e1e95b7dcb859a1c` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |
| `fact-7e4f7e6d5ecd7a76` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0706cfb86d44faf8` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DEN | `` | `S1b_llm_canonicalized:2026-05-20:163:fact-9b7fef728bf2` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-122d4de55840b5a0` | `S2_llm_schema_slice` | `controlledNASelement` | urn:nas:Airport:DEN | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT |
| `cand-181e571abb376ae3` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-20T23:15:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-023:fact-04-a002c4d839d5` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED:... |
| `cand-1929a705ef342d89` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-19bae32975f9db4b` | `S1_llm_only` | `'has_control_element'}` | {'label': 'DEN ELEMENT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-1fcdf3d9db300e34` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DEN | `fact-21c3d59a53f0aa6b` | `fact-21c3d59a53f0aa6b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN |
| `cand-2022703c27378dc2` | `S1_llm_only` | `'tier'}` | {'label': '1stTier'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-35319193695116ac` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-ed8baaabd1233014` | `fact-ed8baaabd1233014` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-40dac55fbb1543a3` | `S0_rule_only` | `impactingCondition` | staffing | `fact-e1e95b7dcb859a1c` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-4eb47e3f307afdd4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T22:00:00Z | `fact-79bf0c09be665285` | `fact-79bf0c09be665285` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 22:00 |
| `cand-4f36ace149a421c9` | `S1_llm_only` | `'has_element_type'}` | {'label': 'APT ADL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-5064f1e4079f118a` | `S1_llm_only` | `'announces_ground_stop_period'}` | {'label': 'ground stop period', 'value': '20/2200Z - 20/2315Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-564b5bc1876a895f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-569d84202a0d06f5` | `S1_llm_only` | `'states_probability_of_extension'}` | {'label': 'probability', 'value': 'MEDIUM'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-5d0abfa3cfed7e01` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-20T22:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-023:fact-03-85df2df91063` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED:... |
| `cand-5d2ead0d40b104d2` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T22:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 22:00 |
| `cand-77d3481493ee545c` | `S1_llm_only` | `'has_effective_time'}` | {'label': 'effective time', 'value': '202159-210015'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-83c548aa70e78d10` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-5d0321f5117109e7` | `fact-5d0321f5117109e7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 202159-210015 SIGNATURE: 26/05/20 22:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-842037af82734de0` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | DEN | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-023:fact-01-83f10fc2425f` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z |
| `cand-8f91309f1e6d40ec` | `S2_llm_schema_slice` | `impactingCondition` | other | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-900cd68f84e1de7f` | `S1b_llm_canonicalized` | `impactingCondition` | impacting condition staffing | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-91a2f4da818bd436` | `S1_llm_only` | `'reports_previous_delays'}` | {'label': 'delay statistics', 'value': '0 / 0 / 0'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-9590366ca49fb019` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 163 | `fact-e424b7a77a4a3134` | `fact-e424b7a77a4a3134` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-97645fb2b11c349f` | `S1_llm_only` | `'reports_new_delays'}` | {'label': 'delay statistics', 'value': '1918 / 74 / 46'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1918 / 74 / 46 |
| `cand-9d4b45b1cec3fb96` | `S1_llm_only` | `'states_impacting_condition'}` | {'label': 'impacting condition', 'value': 'STAFFING'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: |
| `cand-a5aab9c643372e8d` | `S0_rule_only` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-7e4f7e6d5ecd7a76` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-a60bed52369f1505` | `S1_llm_only` | `'includes_departure_facilities'}` | {'label': 'departure facilities included', 'value': 'ZLA ZLC ZDV ZKC ZAB ZMP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-a6922b5593037b5a` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-023:fact-02-9210b33bde02` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 2157Z GROUND STOP PERIOD: 20/2200Z - 20/2315Z DEP FACILITIES INCLUDED:... |
| `cand-c524a918fe25acd9` | `S2_llm_schema_slice` | `withinARTCC` | urn:nas:ARTCCtier:1stTier | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-ca41ec463fbb2a45` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T21:59:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-ca64943abbc77a0c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-cab30bdb1ab660f3` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-cc9e158e5fe5e185` | `S2_llm_schema_slice` | `advisoryNumber` | 163 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-d159a2d13a7436a7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-21T00:15:00Z | `fact-23a4530f1041cd31` | `fact-23a4530f1041cd31` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202159-210015 |
| `cand-d32a31ca6bfa56fc` | `S2_llm_schema_slice` | `departureScope` | urn:airportSpec:2026-05-20:163:departure | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-e320b7906d19af60` | `S2_llm_schema_slice` | `type` | atm:GroundStopTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `cand-e3df139d7267390b` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-21T00:01:15Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202159-210015 |
| `cand-e6b318a76e50badd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T21:59:00Z | `fact-007f06e2f975eeaa` | `fact-007f06e2f975eeaa` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202159-210015 |
| `cand-eec2f9bc9b8ad3a4` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-eefb116bee0bbaa1` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-fe9516fb36c285d8` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |

## ATCSCC-GOLD-001 / 2026-05-19:032

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=76, est=23 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 35
- Cross-system clusters: 34
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=32

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. EFFECTIVE TIME: 191322-191630 SIGNATURE: 26/05/19 13:22 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-5ae87a115b7714a5` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `fact-5ae87a115b7714a5` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03980efdeb6e9215` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-092d47690b54cb8b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THAT | `fact-1925abbdac300f9f` | `fact-1925abbdac300f9f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-0956f4acebbd46c2` | `S1_llm_only` | `has advisory title` | DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-0c293b3a62114ee0` | `S1_llm_only` | `replaces advisory` | 027 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY REPLACES ADVZY 027 |
| `cand-26248cca7b96a8f7` | `S1_llm_only` | `encouraged action` | file alternate routes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES. |
| `cand-2a5e39256de37832` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `fact-39e7946abbfec5fb` | `fact-39e7946abbfec5fb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | _RQD |
| `cand-2eb7db50e5f7e305` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ARE | `fact-d79659753d38bd62` | `fact-d79659753d38bd62` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-3470caf9720e03ce` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T13:22:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-001:fact-02-c326f199df88` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-3e78fc365dd21aee` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-001:fact-06-553df2caf69d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-3e8ed1851904958f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T16:30:00Z | `fact-31ce78158e4d3954` | `fact-31ce78158e4d3954` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191322-191630 |
| `cand-48ee85e1e5be8dd1` | `S1_llm_only` | `cause stated in advisory` | severe turbulence | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-5452139e1194c658` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADVZY | `fact-8512415585cd427c` | `fact-8512415585cd427c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-580069f2df1cb6f9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:AR8 | `fact-175eb3c3d1f1ab96` | `fact-175eb3c3d1f1ab96` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-5f88b556258bb0b4` | `S1b_llm_canonicalized` | `advisoryNumber` | 32 | `` | `S1b_llm_canonicalized:2026-05-19:032:fact-578af7ed6b4b` | `{"repaired_accepted": 1}` | `{}` | ZNY REPLACES ADVZY 027 |
| `cand-61c8e7ec09b3ca1e` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-001:fact-03-05c5cad0250e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-64f6e977c8b8b2b8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T13:22:00Z | `fact-a061bc66894916b5` | `fact-a061bc66894916b5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191322-191630 |
| `cand-665a5be97a6969ae` | `S2_llm_schema_slice` | `advisoryNumber` | 32 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-001:fact-01-83e867e78fbe` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-6db320888d86cf81` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:L454 | `fact-9460e6cc9c541109` | `fact-9460e6cc9c541109` | `{"hybrid_backbone_accepted": 2, "repaired_accepted": 2}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-7ca7a8175b5dcbba` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `fact-5ae87a115b7714a5` | `` | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-7e9c1410238dbb41` | `S1_llm_only` | `effective time` | 191322-191630 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191322-191630 |
| `cand-858a5b29bd3619df` | `S1_llm_only` | `advises route closure` | L452 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-86ca9275f3059e2f` | `S1_llm_only` | `advises route closure` | L454 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-8bca18b88e693850` | `S1_llm_only` | `advises route closure` | AR8 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-8d1b462e960d741a` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-001:fact-04-f96dd6cf4dbe` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-8dfa6e571ced77bf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T13:22:00Z | `fact-fd94fdaec37c4f73` | `fact-fd94fdaec37c4f73` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 13:22 |
| `cand-8f22a524e366583a` | `S1_llm_only` | `reports event time window` | 19/1200 - 19/1600 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/1200 - 19/1600 |
| `cand-9f7c702c3489fb66` | `S1_llm_only` | `names constrained facility` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-a30425c30c41b509` | `S1b_llm_canonicalized` | `impactingCondition` | severe turbulence | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | L452 / AR8 / L454 ARE CLOSED DUE TO SEVERE TURBULENCE. |
| `cand-a3f41e32e500c1e4` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-001:fact-05-af40bb754ab6` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-c03e0e96bf714bf5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADDS | `fact-fa412a843d8bd200` | `fact-fa412a843d8bd200` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-c1de08278625081b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:L452 | `fact-ad56fc9170893f78` | `fact-ad56fc9170893f78` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED |
| `cand-d5044991bcb5608b` | `S1_llm_only` | `adds route` | L454 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADDS L454 |
| `cand-dd73696174e72a7b` | `S2_llm_schema_slice` | `initiativeComments` | EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452 / AR8 / L454 ARE CLOSED DUE... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-001:fact-07-29a52d4041f3` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD MESSAGE: EVENT TIME: 19/1200 - 19/1600 CONSTRAINED FACILITIES: ZNY REPLACES ADVZY 027 ADDS L454 ZNY ADVISES THAT L452... |
| `cand-ec3d65f234308d7e` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 32 | `fact-fed481e8d75d70ab` | `S1b_llm_canonicalized:2026-05-19:032:fact-ada1d79a750b, fact-fed481e8d75d70ab` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD |
| `cand-f581456c98fbad41` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |

## ATCSCC-GOLD-021 / 2026-05-14:089

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=73, est=24 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 34
- Cross-system clusters: 32
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=89

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 089 BNA/ZME 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2220Z GROUND STOP PERIOD: 14/2112Z - 14/2300Z DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 606 / 70 / 23 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1243 / 100 / 48 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 EFFECTIVE TIME: 142224-150000 SIGNATURE: 26/05/14 22:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-3c4247c92836f15f` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |
| `fact-5e0a045d089d24b4` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-07fee9e28fbb285e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-0b27ba3913cff5eb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 89 | `fact-3a9689db576a50a9` | `fact-3a9689db576a50a9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 089 BNA/ZME 05/14/2026 CDM GROUND STOP |
| `cand-0c60b8fbe26c138c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-0d12cb370461296d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-0f40f3edd018c254` | `S1b_llm_canonicalized` | `impactingCondition` | staffing impacting_condition | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-17112c8e38e7fa95` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-279ebb6249912ae1` | `S1_llm_only` | `'relation'}` | {'label': 'MEDIUM', 'type': 'probability_level'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2b5cf5ccc8559c5d` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2220Z GROUND STOP PERIOD: 14/2112Z - 14/2300Z DEP FACILITIES INCLUDED: (Manual) ZAU... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-021:fact-05-2c580d423afc` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 2220Z GROUND STOP PERIOD: 14/2112Z - 14/2300Z DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID PREVIOUS TOTAL,... |
| `cand-2c543cf5f8578bb1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EXTENDED UPDATE TIME OF 2300 | `fact-4d3568cb54fb7081` | `fact-4d3568cb54fb7081` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-2d4299187edb5d15` | `S0_rule_only` | `impactingCondition` | staffing | `fact-3c4247c92836f15f` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-2e294cf308c6f3fe` | `S1_llm_only` | `'relation'}` | {'label': '14/2112Z - 14/2300Z', 'type': 'time_period'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 14/2112Z - 14/2300Z |
| `cand-3613697a48cba1f5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T00:00:00Z | `fact-ffe1d56fce2d6f15` | `fact-ffe1d56fce2d6f15` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-3fce3a58f4cc7b30` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `fact-b40151e58090aefb` | `S1b_llm_canonicalized:2026-05-14:089:fact-89c012fad318, fact-b40151e58090aefb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: BNA |
| `cand-47e111d08ed41660` | `S2_llm_schema_slice` | `initiativeComments` | EXTENDED UPDATE TIME OF 2300 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-021:fact-05-e97747e3dc36` | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-4a1c7dd0530889ee` | `S1_llm_only` | `'relation'}` | {'label': '2300', 'type': 'time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-51f018e66b70d674` | `S1_llm_only` | `'relation'}` | {'label': '1243 / 100 / 48', 'type': 'delay_summary'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1243 / 100 / 48 |
| `cand-5c7b313cbd88caca` | `S1_llm_only` | `'relation'}` | {'label': 'APT ADL', 'type': 'element_type'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-69fab0a4e5c06090` | `S1_llm_only` | `'relation'}` | {'label': 'BNA', 'type': 'airport_element'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-6f704afc8be63698` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-75007d05dcb81810` | `S1_llm_only` | `'relation'}` | {'label': 'ZAU ZTL ZHU ZFW ZKC ZME ZID', 'type': 'facility_list'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-7ee7e216e7c5420e` | `S1_llm_only` | `'relation'}` | {'label': '142224-150000', 'type': 'effective_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 142224-150000 |
| `cand-86fba66a3877c7c0` | `S0_rule_only` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-5e0a045d089d24b4` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-8d509d0f8d6be841` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | nas:Airport:BNA | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-021:fact-01-830b5431ebb5` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-96f3039aa7e0a539` | `S1_llm_only` | `'relation'}` | {'label': '606 / 70 / 23', 'type': 'delay_summary'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 606 / 70 / 23 |
| `cand-97f357231cf50a47` | `S2_llm_schema_slice` | `controlledNASelement` | BNA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-021:fact-01-27dc0a33baab` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-9abe91116e64a3db` | `S0_rule_only, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-0028f560ea4206d8` | `S2_llm_schema_slice:ATCSCC-GOLD-021:fact-02-5cec43a433f6, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-021:fact-02-5cec43a433f6, fact-0028f560ea4206d8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-9eb32a440b4f66ea` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-021:fact-03-419e17f929a3` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING |
| `cand-ad2d06e9d1a627d0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T22:24:00Z | `fact-19cc97c4dbead592` | `fact-19cc97c4dbead592` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-b9f1b5087c191683` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T22:24:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-021:fact-04-ad7c7d71b249` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142224-150000 |
| `cand-c062a36b286f962d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-c46d5275cfd6c61f` | `S1_llm_only` | `'relation'}` | {'label': 'STAFFING', 'type': 'impacting_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-cb09a7d9636ec658` | `S2_llm_schema_slice` | `impactingCondition` | other | `` | `S2_llm_schema_slice:ATCSCC-GOLD-021:fact-03-3761bd1a1689` | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: EXTENDED UPDATE TIME OF 2300 |
| `cand-f3925fe269eef066` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZAU ZTL ZHU ZFW ZKC ZME ZID |
| `cand-f592c62fd6c78f3d` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T22:25:00Z | `fact-6858147ed339bf34` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-021:fact-04-d41dc226e320, fact-6858147ed339bf34` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/14 22:25 |

## ATCSCC-GOLD-005 / 2026-05-19:059

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=70, est=22 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 32
- Cross-system clusters: 31
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=59

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI MESSAGE: EVENT TIME: 19/1645 - 20/0200 CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 191638-200230 SIGNATURE: 26/05/19 16:38 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-f85ffddf4998b783` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |
| `fact-f85ffddf4998b783` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0517cad842649dbd` | `S1_llm_only` | `'identifies constrained facilities'}` | {'label': 'ZHU'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-15984c6fdfc39bac` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `fact-f85ffddf4998b783` | `` | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |
| `cand-1e88b97468decda4` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-2362f4bf93684b17` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T16:38:00Z | `fact-cada0459bfaa3a22` | `fact-cada0459bfaa3a22` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 16:38 |
| `cand-284e30e9e6d4e702` | `S3_llm_schema_slice_validator_repair` | `reRouteType` | CDR | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-2e547f4468922131` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-3764183052dc6352` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'label': 'IAH', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-480afcfebd3554b8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `fact-4c3f6281eea3d2c0` | `fact-4c3f6281eea3d2c0` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZHU ZHU IS IMPLEMENTING CDRS |
| `cand-5186fbd53e9413e4` | `S1_llm_only` | `'states event time'}` | {'label': '19/1645 - 20/0200'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 19/1645 - 20/0200 |
| `cand-59893968d5a5b1eb` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-5caff5616d01f5c7` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-005:fact-04-3f974acb995e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-66f3229b06234ca5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T02:30:00Z | `fact-a8d7137e70a631ca` | `fact-a8d7137e70a631ca` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191638-200230 |
| `cand-671bc36b93bd6cd2` | `S3_llm_schema_slice_validator_repair` | `type` | atm:ReRouteTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-6990fc891f53af26` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T02:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-005:fact-07-c5b7ddc264e7` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-70b4871b899569dc` | `S1_llm_only` | `'reason stated as'}` | {'label': 'weather'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-71dfdccd99e7fea5` | `S1_llm_only` | `'mentions locations'}` | {'label': 'IAH HOU'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-82698dbeb4a7898a` | `S1_llm_only` | `'states effective time'}` | {'label': '191638-200230'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191638-200230 |
| `cand-8a4a2b3375890150` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-19T16:38:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 16:38 |
| `cand-930af7acc8fde85c` | `S2_llm_schema_slice` | `implementationStatus` | FYI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-005:fact-02-36b26b5d0f64` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-9658a4068d877207` | `S2_llm_schema_slice` | `controlledNASelement` | ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-a053fc88bf21f0a2` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T16:38:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-005:fact-05-d55e3953681f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-a3505e8fbde44beb` | `S2_llm_schema_slice` | `advisoryNumber` | 59 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-005:fact-01-2edb8094f187` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-a763979cb20caafd` | `S1_llm_only` | `'gives operational instruction'}` | {'label': 'users should fuel accordingly'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-a832f73d7366847d` | `S3_llm_schema_slice_validator_repair` | `implementationStatus` | FYI | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-ac95c2adb307c435` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 59 | `fact-1d06d8f36d22b07a` | `S1b_llm_canonicalized:2026-05-19:059:fact-14e6f25bf1e0, fact-1d06d8f36d22b07a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-b0b0983cc362175b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T16:38:00Z | `fact-09ed3f826aae59f4` | `fact-09ed3f826aae59f4` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191638-200230 |
| `cand-c7e1fe829757e7ed` | `S2_llm_schema_slice` | `reRouteType` | CDR | `` | `S2_llm_schema_slice:ATCSCC-GOLD-005:fact-03-f9811d9af75a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-d1a227fc020900a8` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 59 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-d4d918e60b2a9bef` | `S3_llm_schema_slice_validator_repair` | `reRouteReason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-d51edf7ad743098d` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'label': 'HOU', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-f26e6771005f30d4` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T16:38:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-005:fact-06-9a13e6610d6e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `cand-f9349a7d3276cb43` | `S1_llm_only` | `'is implementing'}` | {'label': 'CDRS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZHU IS IMPLEMENTING CDRS DUE TO WEATHER. |

## ATCSCC-GOLD-056 / 2026-05-17:041

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=66, est=21 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 30
- Cross-system clusters: 29
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=41

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 171639-172100 SIGNATURE: 26/05/17 16:39 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-81ef27a1e2ff12cd` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `fact-81ef27a1e2ff12cd` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0130c0f2af55b34f` | `S1_llm_only` | `should fuel accordingly` | fuel accordingly | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-047cdf1363aa9181` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-07-68f2a669e466` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-0ce691ecb215afaa` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-17T21:00:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-04-0006dc03d209` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-212ece368b5e51a6` | `S2_llm_schema_slice` | `advisoryNumber` | 41 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-01-08147b5e942b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-270cb0858ed53be0` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-17T16:39:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-03-a06df2ae5f9b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-2d6d8e2b985e3b4b` | `S1_llm_only` | `has effective time` | 171639-172100 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 171639-172100 |
| `cand-3c515e2bd8890af2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADVZY | `fact-9c3743c5baa708d1` | `fact-9c3743c5baa708d1` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-48e6e63ebdaf3e0f` | `S2_llm_schema_slice` | `controlledNASelement` | MIA FLL CDRS_FYI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-08-ac59c4a92247` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-5762bbdc0be294fc` | `S1_llm_only` | `has advisory headline` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI |
| `cand-6216845ee81ca766` | `S2_llm_schema_slice` | `reRouteType` | CDR | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-06-e0e8e216a3be` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-63b53a68002887e4` | `S1_llm_only` | `identifies constrained facilities` | ZMA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-64ed73f7658c4356` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `fact-81ef27a1e2ff12cd` | `` | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-6d960982e3178b43` | `S1_llm_only` | `extends advisory` | ADVZY 024 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-6e831acc15ec051d` | `S1b_llm_canonicalized` | `advisoryNumber` | 41 | `` | `S1b_llm_canonicalized:2026-05-17:041:fact-17972a235bf3` | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-70fc21f4b8ee5223` | `S1_llm_only` | `reason for implementing` | weather | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-729a4480f087ead5` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-056:fact-03-374815ff9a71` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-72f44f3d79a77dcf` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-17T16:39:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-02-ad0e6e432c7f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-7603f2e6a3bbe00e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T16:39:00Z | `fact-412dbd02e9c78cde` | `fact-412dbd02e9c78cde` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 16:39 |
| `cand-7a80c6758561a6fa` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-17T16:39:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-056:fact-02-46d2113dd9b4` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-803e52d4253d7cd7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `fact-31f58be57b74cf79` | `fact-31f58be57b74cf79` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS |
| `cand-999e8d7b8bd05b35` | `S1_llm_only` | `is implementing` | CDRS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-bbf6f2f45812da76` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T16:39:00Z | `fact-8be810ea86b7d0f8` | `fact-8be810ea86b7d0f8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171639-172100 |
| `cand-c186abaaaa0bf8fd` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 41 | `fact-d00fcf5a5f137dfb` | `S1b_llm_canonicalized:2026-05-17:041:fact-65fd66b76b54, fact-d00fcf5a5f137dfb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI |
| `cand-c3dad3e14736ecea` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 41 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-056:fact-01-9ec30a54651c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-c738e0c7cfa4d1d5` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-cfcb12dc37986896` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-d73c3e55d6c185e2` | `S2_llm_schema_slice` | `initiativeComments` | USERS SHOULD FUEL ACCORDINGLY. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-09-d663fdffd896` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-dd40ac896a89c3f6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T21:00:00Z | `fact-33498b888051a52c` | `fact-33498b888051a52c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171639-172100 |
| `cand-ef3e7fbff55b862c` | `S2_llm_schema_slice` | `implementationStatus` | FYI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-056:fact-05-c837c19d5e0b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI MESSAGE: EVENT TIME: 17/1300 - 17/2100 CONSTRAINED FACILITIES: ZMA EXTENDS ADVZY 024 ZMA IS IMPLEMENTING CDRS DUE TO WEATHER. US... |
| `cand-f3724fe995697939` | `S1_llm_only` | `states event time window` | 17/1300 - 17/2100 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 17/1300 - 17/2100 |

## ATCSCC-GOLD-006 / 2026-05-19:144

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `medium` (score=54, est=19 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 24
- Cross-system clusters: 23
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=144

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED MESSAGE: EVENT TIME: 19/2230 - 20/0300 CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. EFFECTIVE TIME: 192220-200330 SIGNATURE: 26/05/19 22:20 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-087bab64f2a43eb4` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `fact-087bab64f2a43eb4` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-04805052cd09aac5` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 144 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-006:fact-01-725be990ae20, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-006:fact-01-725be990ae20` | `{"repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-07fcb2a51ff11716` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T03:30:00Z | `fact-59dd4d4dc496df47` | `fact-59dd4d4dc496df47` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-0e6136a9ee951b64` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T22:20:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-006:fact-02-cae20fa801fa` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 22:20 |
| `cand-20aaa73732c84b2f` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T03:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-006:fact-04-bb4e98651790` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-23192b28e9c65220` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DROP | `fact-ee8775c6394a5147` | `fact-ee8775c6394a5147` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-2cd2d23d5bc07f99` | `S1_llm_only` | `'causes flight plan drop times to be generated from'}` | {'class': 'traffic_management_time', 'label': 'EDCT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-43633790f4569b9a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:HAS | `fact-bc5823860ba50616` | `fact-bc5823860ba50616` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-510ff876261f5354` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 144 | `fact-f8cc5dd8fcd28c1e` | `S1b_llm_canonicalized:2026-05-19:144:fact-507e64aa140f, fact-f8cc5dd8fcd28c1e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-5187786950bf28bb` | `S2_llm_schema_slice` | `initiativeComments` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFEC... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-006:fact-06-2478d3f55794` | `{"repaired_accepted": 1}` | `{}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED... |
| `cand-532c30b99c554ecc` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T22:20:00Z | `fact-556e847bb8afa02c` | `fact-556e847bb8afa02c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-6ed0a8b756a2cd15` | `S1_llm_only` | `'has implemented'}` | {'class': 'operational_procedure', 'label': 'extended flight plan drop times'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-71e5beec96521a52` | `S1b_llm_canonicalized` | `impactingCondition` | edct | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-72a5ec1771afe01a` | `S2_llm_schema_slice` | `controlledNASelement` | ZBW | `` | `S2_llm_schema_slice:ATCSCC-GOLD-006:fact-05-9c4683d73492` | `{"repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW |
| `cand-7f528fc47a311528` | `S1_llm_only` | `'triggered by condition'}` | {'class': 'unspecified_cause', 'label': 'XXX'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. |
| `cand-878c9beec21df694` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PLAN | `fact-6ef2a5e889c9e0b6` | `fact-6ef2a5e889c9e0b6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-889de63fe5b6bfea` | `S1_llm_only` | `'set to duration'}` | {'class': 'time_duration', 'label': '180 minutes'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-8941d7b4003417d3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:TIMES | `fact-46038ab478518964` | `fact-46038ab478518964` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-a54d42868f9a3c8b` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `fact-087bab64f2a43eb4` | `` | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZBW ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES |
| `cand-a5f63fb15fa09b2c` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | ZBW HAS IMPLEMENTED EXTENDED FLIGHT PLAN DROP TIMES TO 180 MINUTES DUE TO XXX. NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFEC... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-006:fact-03-3823df6625b5` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-a7c0f23db3ee4f27` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T22:20:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-006:fact-03-55816b6c7a90` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192220-200330 |
| `cand-b3fbdcb7ad0f28bc` | `S1_llm_only` | `'are generated from'}` | {'class': 'traffic_management_time', 'label': 'EDCT'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NOTE: IF A GROUND STOP OR GROUND DELAY PROGRAM IS IN EFFECT, FLIGHT PLAN DROP TIMES ARE GENERATED FROM THE EDCT. |
| `cand-b846a5b4b5b8a624` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-19T22:20:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-006:fact-02-e0e40551bda9` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-e9e3b11500230eb2` | `S1_llm_only` | `'announces'}` | {'class': 'operational_action', 'label': 'extended flight plan drop times implemented'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `cand-fe10f1cc9f81bc7b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T22:20:00Z | `fact-c82ec69f828688f7` | `fact-c82ec69f828688f7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 22:20 |

## ATCSCC-GOLD-007 / 2026-05-16:051

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `medium` (score=54, est=18 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 24
- Cross-system clusters: 23
- Rejected facts: 2
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=51

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI MESSAGE: EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. EFFECTIVE TIME: 161818-162330 SIGNATURE: 26/05/16 18:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-fc668d4f79615625` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |
| `fact-fc668d4f79615625` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0c088a95e7679b2c` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-110225132c4a0b95` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-16T18:18:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-03-ffa8016802e7` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-15ebd3b576826e70` | `S2_llm_schema_slice` | `controlledNASelement` | nas:ARTCC/DCC | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-08-19854373c45d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-219764c5542242ba` | `S1_llm_only` | `instruction` | fuel accordingly | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS SHOULD FUEL ACCORDINGLY. |
| `cand-332f96f27ff8beef` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-16T18:18:00Z | `fact-98e9e334f172ead5` | `fact-98e9e334f172ead5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 18:18 |
| `cand-40dffe40a1f1dab8` | `S1_llm_only` | `identifies_constrained_facility` | ZDV | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZDV |
| `cand-4e533db99ede08c6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDRS | `fact-daf03b5e94a43797` | `fact-daf03b5e94a43797` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |
| `cand-4fb8b477200680d2` | `S1_llm_only` | `is_implementing` | CDRS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-4ff32413bc899986` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-09-756a7f126039, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-007:fact-03-756a7f126039` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-5ea2f433986c589d` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `fact-fc668d4f79615625` | `` | `{"rejected_schema": 2}` | `{"range_violation": 2}` | CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS |
| `cand-8420637a7cd9ed9e` | `S2_llm_schema_slice` | `advisoryNumber` | 51 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-01-112baff5062e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-88dcd1805977bd29` | `S1_llm_only` | `states_effective_time_window` | 161818-162330 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161818-162330 |
| `cand-8d39633573e323b4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-16T23:30:00Z | `fact-5a7d83086101ccdd` | `fact-5a7d83086101ccdd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-968cbd944ded5179` | `S1_llm_only` | `has_reason` | weather | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. |
| `cand-9d8a1af80687c131` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteType` | CDR | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-06-064f975e82e6, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-007:fact-02-064f975e82e6` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-a7ef25f094c64770` | `S2_llm_schema_slice` | `controlledNASelement` | nas:ARTCC/ZDV | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-07-73f0ead9b75d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-ad7c43de63c7f183` | `S2_llm_schema_slice` | `initiativeComments` | EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-10-a0cb6d0edca9` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 16/1818 - 16/2300 CONSTRAINED FACILITIES: ZDV ZDV IS IMPLEMENTING CDRS DUE TO WEATHER. USERS SHOULD FUEL ACCORDINGLY. |
| `cand-adb4df67cbb52ff9` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-16T23:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-04-1ab9e239b32f` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-be0993666da8b7e4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 51 | `fact-c7bc88238c112d13` | `fact-c7bc88238c112d13` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-c7a09d343923fb39` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `implementationStatus` | FYI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-05-3c6f96ba6267, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-007:fact-01-3c6f96ba6267` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `cand-c96f1aa8e96010a0` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-16T18:18:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-007:fact-02-dd4bcad43a4e` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 18:18 |
| `cand-d0acc6f7a4bc1f7e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-16T18:18:00Z | `fact-03d180d3be3b0e91` | `fact-03d180d3be3b0e91` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161818-162330 |
| `cand-e1c52dcc55e64299` | `S1_llm_only` | `states_event_time_window` | 16/1818 - 16/2300 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 16/1818 - 16/2300 |
| `cand-e4ee9f8f5182942e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZDV |

## ATCSCC-GOLD-018 / 2026-05-19:074

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=127, est=34 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 62
- Cross-system clusters: 61
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=74

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0459Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0459Z ANTICIPATED PROGRAM RATE: 28/18/18/20/20/20/20/20/20 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME ANTICIPATED MAXIMUM DELAY: 175 ANTICIPATED AVERAGE DELAY: 109 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-f72cd5658433c79b` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02508c216bdb419f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-0281167799de88a4` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T18:41:00Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_subject_class": 1}` | SIGNATURE: 26/05/19 18:41 |
| `cand-0ff7e37652936261` | `S1b_llm_canonicalized` | `impactingCondition` | staffing operational_condition | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-15e9936f24603ba9` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-17815b7293fda9d2` | `S1_llm_only` | `'has_departure_scope'}` | {'label': '(ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP', 'type': 'departure_scope'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-1acc7540475d6c7f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-40d8838e8c977a8d` | `fact-40d8838e8c977a8d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-1e5fe1c3b928a3ab` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-19T19:18:40Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-018:fact-04-6806f8a31ed0` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED F... |
| `cand-2827abd6f634c58e` | `S2_llm_schema_slice` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. |
| `cand-284f9972b6e2cd7a` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-2aa3d90864631373` | `S1_llm_only` | `'includes_flights'}` | {'label': 'ALL CONTIGUOUS US DEP', 'type': 'flight_scope'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-32894f05fb2562f0` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z |
| `cand-3718d2a15e1f9902` | `S1_llm_only` | `'is_controlled_by'}` | {'label': 'BNA Element', 'type': 'control_element'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-3a59eb7b60220e11` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-3e8d9c08a488cda3` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-40e53236fb4664e5` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | BNA | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-018:fact-01-4a81dc31e155` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED F... |
| `cand-45aefad73d81f2f1` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-48ce12e5c609eacc` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-4ebef2a9aa80adad` | `S1_llm_only` | `'applies_to'}` | {'label': 'ZME', 'type': 'air_traffic_control_center'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-5c9458e452af4bc0` | `S1_llm_only` | `'has_anticipated_maximum_delay_minutes'}` | {'label': '175', 'type': 'duration_minutes'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 175 |
| `cand-5fd3c948d0031fae` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T18:40:00Z | `fact-0da6d551cd4ad660` | `fact-0da6d551cd4ad660` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191840-191959 |
| `cand-60a31981f152c306` | `S1_llm_only` | `'has_anticipated_program_rate_sequence'}` | {'label': '28/18/18/20/20/20/20/20/20', 'type': 'rate_sequence'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 28/18/18/20/20/20/20/20/20 |
| `cand-64611625348ec576` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-6a34623cd1a05992` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-70a3c1d8303b7c69` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:NONE | `` | `S1b_llm_canonicalized:2026-05-19:074:fact-f1cb32e0390a` | `{"repaired_accepted": 1}` | `{}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-73b74195cfab37e2` | `S1_llm_only` | `'must_be_received_by'}` | {'label': '19/1850Z', 'type': 'deadline_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 19/1850Z |
| `cand-7662122f956e152e` | `S1_llm_only` | `'has_adl_time'}` | {'label': '1836Z', 'type': 'zulu_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1836Z |
| `cand-77f2ec38e8a2147e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-80567684730353f0` | `S1_llm_only` | `'has_anticipated_average_delay_minutes'}` | {'label': '109', 'type': 'duration_minutes'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 109 |
| `cand-81689fd2f24c9704` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T18:41:00Z | `fact-1d56f67c73be3293` | `fact-1d56f67c73be3293` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 18:41 |
| `cand-822cfab1c171d036` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-19T18:41:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-018:fact-07-ea2b585aff7b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED F... |
| `cand-844e0803bfbb0732` | `S3_llm_schema_slice_validator_repair` | `departureScope` | {"atm:includesAirport": [{"label": "ZLA", "type": "nas:Airport"}, {"label": "ZAU", "type": "nas:Airport"}, {"label": "ZLC", "type": "nas:... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-018:fact-02-766bada1f24b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED F... |
| `cand-872163389058bc36` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-87adf0faad9e6dc4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `fact-f1391cc9a8346b44` | `fact-f1391cc9a8346b44` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-890795ff6cf24805` | `S1_llm_only` | `'has_impacting_condition'}` | {'label': 'STAFFING', 'type': 'operational_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-9260f04c80546951` | `S2_llm_schema_slice` | `initiativeComments` | BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES MUST BE RECEIVED BY: 19/1850Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES MUST BE RECEIVED BY: 19/1850Z |
| `cand-93752eb2954d05cb` | `S1_llm_only` | `'has_anticipated_cumulative_program_period'}` | {'label': '19/2030Z - 20/0459Z', 'type': 'time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0459Z |
| `cand-9829c138232de47f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-9aa1ffe762fc741c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-9c0e213c62f6ea57` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T19:59:00Z | `fact-992737fa801f0d2d` | `fact-992737fa801f0d2d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191840-191959 |
| `cand-a34439da370eda18` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T19:18:40Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_subject_class": 1}` | EFFECTIVE TIME: 191840-191959 |
| `cand-a420f8c08a9e9c26` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-19T19:19:59Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-018:fact-03-4affe89d27b4` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED F... |
| `cand-a942ec4d7d1ca0bc` | `S1_llm_only` | `'effective_time_window'}` | {'label': '191840-191959', 'type': 'effective_time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191840-191959 |
| `cand-ac5b18f3df6c7f86` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 74 | `fact-8cc042af4c570dea` | `S1b_llm_canonicalized:2026-05-19:074:fact-2cc87dce543c, fact-8cc042af4c570dea` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-aec6c0fb43fe6264` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-b061fcd565494414` | `S1_llm_only` | `'will_be_in_configuration'}` | {'label': 'TRACAB configuration', 'type': 'airport_configuration'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. |
| `cand-b77c88a073e3e2ef` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-b826267130f7c3ef` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T19:19:59Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_subject_class": 1}` | EFFECTIVE TIME: 191840-191959 |
| `cand-ba234298e34ff62f` | `S1_llm_only` | `'uses_delay_assignment_mode'}` | {'label': 'UDP', 'type': 'delay_assignment_mode'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-be20fb1f7a01b388` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-c31d31867d1efe4b` | `S1_llm_only` | `'announces_program'}` | {'label': 'CDM Proposed Ground Delay Program', 'type': 'traffic_management_program'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-d07068e727647301` | `S3_llm_schema_slice_validator_repair` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED F... |
| `cand-d0d69599a35388dd` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-d37066d3e36ed6c9` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-e05447bce6d6898c` | `S1_llm_only` | `'includes_canadian_departure_airports'}` | {'label': 'NONE', 'type': 'airport_list'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-e1fb21e593da6ce1` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZSE | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-e4921b7fa1b56738` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES MUST BE RECEIVED BY: 19/1850Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-018:fact-06-96b2de72e7ec` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1836Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED F... |
| `cand-ebb0067ff1042007` | `S1_llm_only` | `'scheduled_at'}` | {'label': '1850Z', 'type': 'zulu_time'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONFERENCE AT 1850Z |
| `cand-efd0994c477091ea` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-f1c553fc366327aa` | `S1_llm_only` | `'has_element_type'}` | {'label': 'APT ADL', 'type': 'element_type'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-f1ca9f648e36d4f8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES MUST BE RECEIVED BY: 19/1850Z | `fact-e376537e3483b644` | `fact-e376537e3483b644` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: BNA WILL BE IN A TRACAB CONFIGURATION STARTING IN 00Z. CONFERENCE AT 1850Z USER UPDATES MUST BE RECEIVED BY: 19/1850Z |
| `cand-f2dbab2cb607623c` | `S0_rule_only` | `impactingCondition` | staffing | `fact-f72cd5658433c79b` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-fab60f0453b1b236` | `S1_llm_only` | `'estimated_for_time_window'}` | {'label': '19/2030Z - 20/0459Z', 'type': 'time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0459Z |

## ATCSCC-GOLD-010 / 2026-05-20:053

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=96, est=27 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 46
- Cross-system clusters: 46
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=53

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201700 PROBABILITY OF EXTENSION: MODERATE REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < REDDN4 TMI ID: RRDCC504 EFFECTIVE TIME: 201000-201700 SIGNATURE: 26/05/20 12:48 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| C...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-4f4cfb688f7b6af0` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0e34ab120d1c0f88` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-12-6c65325b5b26` | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STAT... |
| `cand-23c53352b6f57970` | `S0_rule_only, S1b_llm_canonicalized` | `extensionProbability` | MODERATE | `fact-4f4cfb688f7b6af0` | `` | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-2796068438874849` | `S3_llm_schema_slice_validator_repair` | `implementationStatus` | RQD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-01-e7f059837b91` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-3147d2bc3c99fb1b` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-31d7569c24391a8f` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-11-f255a1def1a5` | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STAT... |
| `cand-32a45098e70cf94f` | `S3_llm_schema_slice_validator_repair` | `reRouteReason` | WEATHER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-02-5287199f7ab5` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-38efe07fbb569e1c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-4c63d776ff1ba302` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-01-e02b66a8057f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-4d243e73d8ee2637` | `S1_llm_only` | `has_reason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-51e16de460e365c5` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-09-85bd93a309b4` | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STAT... |
| `cand-5d968ed5fc68468f` | `S1_llm_only` | `valid_from` | 201000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201700 |
| `cand-63a04c722f0d412e` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-04-784e30b3e77a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-672a6392c904970a` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T12:48:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-05-4d617efe7254` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-6c7e9b9bba843607` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T20:10:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-07-09fb05afe460` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-81cba67748da78d3` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-888fa66ea6c40581` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 53 | `fact-dd507a10b266a207` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-06-d6bb682e53d5, fact-dd507a10b266a207` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-937f8f3fecf9545b` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-10-ae1a10a98513` | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STAT... |
| `cand-9ed23d71fb84d59b` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-20T17:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-08-8909f69ed29c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-9f5fc1dcf334f02c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T17:00:00Z | `fact-d4cb58a3057f91fc` | `fact-d4cb58a3057f91fc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201700 |
| `cand-a6aee0d5d0d3cfde` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-a9fce8d43f2bffe3` | `S2_llm_schema_slice` | `initiativeComments` | REPLACES ADVZY 042, EXTENDS END TIME. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-13-c2aea7b22669` | `{"repaired_accepted": 1}` | `{}` | NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STAT... |
| `cand-ae01b2d49eebda77` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-04-cdc26a515f45` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-b7445d154db243e8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T10:00:00Z | `fact-0a36b9777dab4f63` | `fact-0a36b9777dab4f63` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201700 |
| `cand-ba13444684174556` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-ba2fe74ef9dcaecc` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-bbbf26e5771f305a` | `S1_llm_only` | `valid_to` | 201700 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201700 |
| `cand-bc7d2c9195ad7ad6` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T21:70:00Z | `` | `` | `{"rejected_schema": 1}` | `{"datatype_value_not_datetime": 1}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-bc89c9601d92aee8` | `S1_llm_only` | `has_constrained_area` | ZHU | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZHU |
| `cand-bcf12693b24285f5` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-03-d564af12863e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-bf003dc3fe2121d9` | `S1_llm_only` | `includes_traffic` | KMCO/KORL/KSFB/ZMA departures to KDAL/KDFW | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-c987225a8def3deb` | `S3_llm_schema_slice_validator_repair` | `reRouteType` | ROUTE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-03-c85a9739b66d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-cb10468ef23ec5db` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T12:48:00Z | `fact-bce20432fb829854` | `fact-bce20432fb829854` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 12:48 |
| `cand-cc1e4f5b7bed5f0f` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-20T12:48:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-06-6444c7dc9630` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-cc8610ff36466fb3` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-20T20:10:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-07-1d163ddfb344` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-cfe262958628eb81` | `S1_llm_only` | `has_probability_of_extension` | MODERATE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-d52232757d2a9709` | `S1_llm_only` | `replaces_advisory` | ADVZY 042 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-d550f6cf56ce61f6` | `S1_llm_only` | `has_flight_status` | ALL_FLIGHTS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-da22912b0e79a270` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-e7cec40e0b2251a6` | `S1_llm_only` | `is_named` | FLORIDA_TO_TEXAS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: FLORIDA_TO_TEXAS |
| `cand-ecbdbad34f80facf` | `S1_llm_only` | `has_effective_time_range` | 201000-201700 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201000-201700 |
| `cand-efcb10fc1b6a4d21` | `S1b_llm_canonicalized` | `advisoryNumber` | 53 | `` | `S1b_llm_canonicalized:2026-05-20:053:fact-876187c735ec` | `{"repaired_accepted": 1}` | `{}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-f267f6ac5624b821` | `S1_llm_only` | `has_facilities_included` | ZFW/ZHU/ZJX/ZMA/ZME/ZTL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-f3558c62a10d7ece` | `S1_llm_only` | `extends_end_time` | true | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 042, EXTENDS END TIME. |
| `cand-f563ac8dc2cdde21` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | REPLACES ADVZY 042, EXTENDS END TIME. | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-010:fact-05-14fede260208` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW F... |
| `cand-f747e6a3206f52b2` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-010:fact-02-477e0b1c2150` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-fcfa79f240a9db1a` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |

## ATCSCC-GOLD-014 / 2026-05-18:104

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=96, est=27 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 46
- Cross-system clusters: 46
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=104

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 182000 TO 190000 PROBABILITY OF EXTENSION: MODERATE REMARKS: AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK < KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK < BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK < BENKY6 ZME KORD >MEMFS RZC BUM IRK < BENKY6 TMI ID: RRDCC511 EFFECTIVE TIME: 182000-190000 SIGNATURE: 26/05...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-8aae295140e88a1f` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-003286a339cbb1d8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 104 | `fact-ed0d8124b24bf76e` | `fact-ed0d8124b24bf76e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-025f92442ae79487` | `S3_llm_schema_slice_validator_repair` | `reRouteReason` | WEATHER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-04-1d9ccee73954` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-02ff09fb89986d70` | `S1_llm_only` | `has identifier` | RRDCC511 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 TMI ID: RRDCC511 |
| `cand-05402a926798c4b0` | `S1_llm_only` | `routes via` | BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK |
| `cand-1950a055bd8003b1` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-05-7c603bfd72fa` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-1f3d2c63fdc1cdeb` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 104 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-01-9c2c6892ccff` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-21b20011dc7113d6` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | nas:Airport | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-09-ad39817eb21c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-3230aabe61f418c1` | `S1_llm_only` | `has flight status` | ALL_FLIGHTS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-33f8a31b46354af4` | `S2_llm_schema_slice` | `advisoryNumber` | 104 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-3418e2806fe858ed` | `S1_llm_only` | `has constrained area` | ZID/ZOB | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB |
| `cand-348a3fb61f3f9d30` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `fact-aee850ee61a40918` | `fact-aee850ee61a40918` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-3554a6917b4073a3` | `S1_llm_only` | `routes to destination KORD via` | VLKNN MEMFS RZC BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-3e8404680efcc7a3` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-4cdca620e4ea5888` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-503a5683d10e4249` | `S1_llm_only` | `includes traffic` | KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME departures to KORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-52b81223d7f091cf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T20:00:00Z | `fact-177a9f5ac8c83678` | `fact-177a9f5ac8c83678` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-55b784ec68633df3` | `S1_llm_only` | `is valid during` | ETD 182000 TO 190000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-5a0ac10d82250fc0` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-5d93869d80c360a0` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-5ea65a80c7197973` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T19:18:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 19:18 |
| `cand-5ff1e690b3020817` | `S3_llm_schema_slice_validator_repair` | `implementationStatus` | RQD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-02-f0ca434e5504` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-75f465d9032fa72b` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-18T18:20:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-06-1641172411cd` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-79d730a2bda72da9` | `S1_llm_only` | `routes to destination KORD via` | JAWJA Q116 VLKNN MEMFS RZC BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK |
| `cand-8adc887a325515f8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T19:18:00Z | `fact-90c3e4836d43ae46` | `fact-90c3e4836d43ae46` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 19:18 |
| `cand-8c6aa8fe9ddec28e` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T18:20:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-93660c8e43eff32a` | `S1_llm_only` | `has effective time` | 182000-190000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182000-190000 |
| `cand-96f431725336fd25` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T19:00:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-97cd6aa08127117f` | `S2_llm_schema_slice` | `initiativeComments` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM I... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | REMARKS: AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK < KJAX BENKY6 ZJX(-CAE -CHS... |
| `cand-97e1ea2165f3584c` | `S1_llm_only` | `has remarks` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: AD-HOC ROUTING ASSOCIATED RESTRICTIONS |
| `cand-a6a0fd33e39f7596` | `S2_llm_schema_slice` | `controlledNASelement` | KORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-acce14a9720152fa` | `S1_llm_only` | `has probability of extension` | MODERATE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-b58cec8da1e7d3e5` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-c162497a47f9d84e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-c1a8c55a270dc8c4` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-c8e41bc3d3964c7c` | `S0_rule_only, S1b_llm_canonicalized` | `extensionProbability` | MODERATE | `fact-8aae295140e88a1f` | `` | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-cb8c72ed3269b2a9` | `S2_llm_schema_slice` | `controlledNASelement` | ZID/ZOB | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZID/ZOB |
| `cand-cc7c291cad354dd5` | `S1_llm_only` | `routes to destination KORD via` | MEMFS RZC BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZME KORD >MEMFS RZC BUM IRK |
| `cand-cf99829a008a9b07` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-cf9f2dcd7b93d9b1` | `S1_llm_only` | `has included facilities` | ZAU/ZJX/ZKC/ZMA/ZME/ZTL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-d0033b9c41a9e822` | `S3_llm_schema_slice_validator_repair` | `reRouteType` | ROUTE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-03-8d68534f7411` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-da74e9d00b5dbacd` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | AD-HOC ROUTING | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-08-a611e891d7fd` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-e175671a058f7c45` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-e369ca4a4eaf225d` | `S1_llm_only` | `has reason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-e39f8676885d97d8` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-18T19:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-014:fact-07-1a2fb93e74ba` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTUR... |
| `cand-ec1d073503370420` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-fad0d5e3bb5e1309` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |

## ATCSCC-GOLD-011 / 2026-05-19:108

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=94, est=27 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 45
- Cross-system clusters: 45
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=108

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL MESSAGE: NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 192115 TO 200000 PROBABILITY OF EXTENSION: MODERATE REMARKS: FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST HIGHER ALTITUDE. JETS=10000 ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KBOS KJFK >BURDY T358 SEY ARCAV ORCHA CCC V46 DPK JFK < KBOS KHPN >BOSOX T303 MAD EEGOR < EEGOR1 KBOS KLGA >BOSOX T303 MAD EEGOR PRENO < KBOS KDXR >BOSOX T303 MAD EEGOR < EEGOR1 KBOS KEWR KTEB KMMU >BOSOX T303 HFD...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-966e3093dbe89e25` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0ab46595d74b8051` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteType` | ROUTE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-05-3580b06e82ac` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-0aedf634bbeba826` | `S1_llm_only` | `effective_time` | 192115-200000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192115-200000 |
| `cand-11d85479d2dcf3b2` | `S2_llm_schema_slice` | `extensionProbability` | {'type': 'xsd:string', 'value': 'MEDIUM'} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT... |
| `cand-142b21005ca21926` | `S1_llm_only` | `is_valid_from_to` | ETD 192115 to 200000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 192115 TO 200000 |
| `cand-1def5808ae092bb5` | `S2_llm_schema_slice` | `reRouteReason` | {'type': 'xsd:string', 'value': 'WEATHER'} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT... |
| `cand-222d55315f21d765` | `S1_llm_only` | `applies_to_flight_status` | ALL_FLIGHTS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-25260d9f06332193` | `S2_llm_schema_slice` | `controlledNASelement` | {'type': 'nas:ARTCC', 'value': 'ZNY'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT... |
| `cand-2905f0aa1c7cda52` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T21:06:00Z | `fact-5678f4374af43fc2` | `fact-5678f4374af43fc2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:06 |
| `cand-2cac6859add476fc` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZBW/ZNY |
| `cand-2eec846f7d5c5280` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-07-8e877f332821` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-355d565d91817c46` | `S1_llm_only` | `has_constrained_area` | ZBW | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZBW |
| `cand-37b8da991f9d6734` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T21:15:00Z | `fact-4826d197135d1806` | `fact-4826d197135d1806` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192115-200000 |
| `cand-3af0e90a5901df39` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZBW/ZNY |
| `cand-3b6603fb86799e13` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-19T20:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-03-14a87d45e443` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192115-200000 |
| `cand-3bcd2c60adb99690` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteReason` | WEATHER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-06-76867dd1dd87` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER |
| `cand-3defa7df9bf196f0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T00:00:00Z | `fact-93d15dfca9d8a543` | `fact-93d15dfca9d8a543` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192115-200000 |
| `cand-41fb01f32b8668bc` | `S1_llm_only` | `uses_route` | BOSOX T303 HFD V3 CMK V623 KCDW KLDJ SAX | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KEWR KTEB KMMU >BOSOX T303 HFD V3 CMK V623 KCDW KLDJ SAX |
| `cand-454c2460d012200e` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZBW/ZNY |
| `cand-458a66d47a28fe19` | `S2_llm_schema_slice` | `effectiveStartTime` | {'type': 'xsd:dateTime', 'value': '2026-05-19T19:21:15Z'} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192115-200000 |
| `cand-554964be27c43c2c` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST HIGHER ALTITUDE. JETS=10000 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-11-5774eb220cac` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | REMARKS: FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST HIGHER ALTITUDE. JETS=10000 |
| `cand-55d5b3c30389e32d` | `S2_llm_schema_slice` | `controlledNASelement` | {'type': 'nas:ARTCC', 'value': 'ZBW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL CONSTRAINED AREA: ZBW REASON: WEATHER INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB FACILITIES INCLUDED: ZBW/ZNY FLIGHT... |
| `cand-5d8870c0c1872c9f` | `S1_llm_only` | `must_comply_with` | altitude restrictions | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. |
| `cand-71d0dcf21d077858` | `S2_llm_schema_slice` | `advisoryNumber` | {'type': 'xsd:integer', 'value': 108} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-7cce48ddfb502345` | `S0_rule_only, S1b_llm_canonicalized` | `extensionProbability` | MODERATE | `fact-966e3093dbe89e25` | `` | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-801b2dce5b9df140` | `S1_llm_only` | `has_reason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-808673442fb79b71` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-88756da0b2a83f32` | `S1_llm_only` | `includes_facilities` | ZBW/ZNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZBW/ZNY |
| `cand-8fa09079f7e84bca` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 108 | `fact-93fead9cc7da4d71` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-01-69ac654583c8, fact-93fead9cc7da4d71` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-90e971656cd723f9` | `S1_llm_only` | `has_maximum_altitude` | 10000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | JETS=10000 |
| `cand-9217ff66a3b547a1` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZBW/ZNY |
| `cand-9b7503ec77d0dca2` | `S2_llm_schema_slice` | `issuedTime` | {'type': 'xsd:dateTime', 'value': '2026-05-19T21:06:00Z'} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/19 21:06 |
| `cand-c3e85f77a332b09d` | `S1_llm_only` | `uses_route` | BOSOX T303 MAD EEGOR PRENO | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KLGA >BOSOX T303 MAD EEGOR PRENO |
| `cand-cc498f244beed8f5` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-19T19:21:15 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-02-520069dc4794` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192115-200000 |
| `cand-d24682a836b8107e` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED AREA: ZBW |
| `cand-d3284c1ac70979ca` | `S1_llm_only` | `must_not_request` | higher altitude | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DO NOT REQUEST HIGHER ALTITUDE. |
| `cand-d4153188d033620a` | `S1_llm_only` | `uses_route` | BURDY T358 SEY ARCAV ORCHA CCC V46 DPK JFK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KJFK >BURDY T358 SEY ARCAV ORCHA CCC V46 DPK JFK |
| `cand-dcdf6ca9966268e0` | `S1_llm_only` | `includes_traffic` | KBOS departures to KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KBOS DEPARTURES TO KCDW/KDXR/KEWR/KHPN/KJFK/KLDJ/KLGA/KMMU/KTEB |
| `cand-e6a99e8dcb333b85` | `S2_llm_schema_slice` | `implementationStatus` | {'type': 'xsd:string', 'value': 'RQD'} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-e7127bf5fbb53ae2` | `S1_llm_only` | `uses_route` | BOSOX T303 MAD EEGOR | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KDXR >BOSOX T303 MAD EEGOR |
| `cand-e9f95a6e1445d37b` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-011:fact-04-5c7745b68daa` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-ed85ecfe71d30247` | `S1_llm_only` | `uses_route` | BOSOX T303 MAD EEGOR | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KBOS KHPN >BOSOX T303 MAD EEGOR |
| `cand-ede10f35ad871569` | `S1_llm_only` | `is_named` | SERBOS_1_PARTIAL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: SERBOS_1_PARTIAL |
| `cand-f11f56ceda2b8b42` | `S2_llm_schema_slice` | `reRouteType` | {'type': 'xsd:string', 'value': 'ROUTE'} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `cand-f1366fdf5016b462` | `S2_llm_schema_slice` | `effectiveEndTime` | {'type': 'xsd:dateTime', 'value': '2026-05-19T20:00:00Z'} | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192115-200000 |
| `cand-f906cd015a6349c7` | `S1_llm_only` | `has_probability_of_extension` | MODERATE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_fact_type": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |

## ATCSCC-GOLD-052 / 2026-05-20:119

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=91, est=26 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 44
- Cross-system clusters: 43
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=119

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-4e225078b5406aa3` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01eea5f8c4d88719` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-02716181d6815eda` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-03b5b7f1ad989dc8` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-052:fact-03-bff3a7b7c6fc` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED:... |
| `cand-082a201b8e9db57c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-0a617697bbff5dcc` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAD | `` | `S1b_llm_canonicalized:2026-05-20:119:fact-164b0adc9335` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM... |
| `cand-0ff17c32dde7dada` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-1c3d7d678f65b530` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZTL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-1da7a2b517a92b02` | `S1_llm_only` | `'has_impacting_condition'}` | {'class': 'weather_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1f1e7f7a30461cc0` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-2161dafd31b53a65` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZOB'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-25342a04d7d03dea` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZBW'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-295e19bfccb226b2` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-2c0a1426cea1945e` | `S1_llm_only` | `'has_control_element'}` | {'class': 'airport', 'text': 'IAD'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM... |
| `cand-3549fb9b0978f4fd` | `S1_llm_only` | `'identifies_facility_area'}` | {'class': 'facility_area', 'text': 'ZDC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-5273f5dab86b7c6c` | `S1_llm_only` | `'reports_new_average_delay_minutes'}` | {'class': 'delay_minutes_average', 'text': '48'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-532a0b4229d58b99` | `S1_llm_only` | `'has_ground_stop_period'}` | {'class': 'time_window', 'text': '20/1900Z - 20/2015Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM... |
| `cand-62591f2fdf6257e9` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-052:fact-02-d25ec675317a` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED:... |
| `cand-6aac46489f046a31` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-53a4c1c3ee144cfe` | `S2_llm_schema_slice:ATCSCC-GOLD-052:fact-03-5c80a1a8cf26, fact-53a4c1c3ee144cfe` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-78f7a838e381a1a0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAD | `fact-5a273ab03b0bee34` | `fact-5a273ab03b0bee34` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD |
| `cand-79c9b6e13662e986` | `S1_llm_only` | `'states_probability_of_extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-7a7cb21f798b4df4` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-189f9de760a2f7ae` | `S1b_llm_canonicalized:2026-05-20:119:fact-bcfe1e4b7526, S2_llm_schema_slice:ATCSCC-GOLD-052:fact-02-b92e6d8601d8, fact-189f9de760a2f7ae` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-878c7af4e7d57082` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T19:12:00Z | `fact-794f7a6917c57eaa` | `S2_llm_schema_slice:ATCSCC-GOLD-052:fact-04-d4ecb4b1f63f, fact-794f7a6917c57eaa` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/20 19:12 |
| `cand-883ccd0df13b5475` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-9554892111372a78` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T21:15:00Z | `fact-a707de3de8c83236` | `fact-a707de3de8c83236` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201911-202115 |
| `cand-a1934673633dc56f` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZJX'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-a7d9c96bebdf59fe` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZDC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-b8ec95a2eae0238d` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZID'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-b9f8a5d6dfc97aba` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-20T20:15:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-052:fact-05-483a39ef81bc` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED:... |
| `cand-bc86be0369f68cdf` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | {"evidence_text": "CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z", "type": "nas:Airport"} | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-052:fact-01-128bd6a1402b` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z |
| `cand-c221711026fdba3c` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T20:15:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-052:fact-07-28c69e3bccee` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/1900Z - 20/2015Z |
| `cand-c2748b7b9c752373` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'air_traffic_facility', 'text': 'ZNY'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-c475f7cf954c0431` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-c804b66d3672c62a` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 119 | `fact-5294a951d6a4ecde` | `S1b_llm_canonicalized:2026-05-20:119:fact-52044869d049, S2_llm_schema_slice:ATCSCC-GOLD-052:fact-05-3e9f91cbc5df, fact-5294a951d6a4ecde` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-cdcbf196db45c224` | `S1_llm_only` | `'announces_ground_stop'}` | {'class': 'traffic_management_action', 'text': 'CDM GROUND STOP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-ce3ad729b93e52a3` | `S1_llm_only` | `'reports_new_total_delay_minutes'}` | {'class': 'delay_minutes_total', 'text': '1939'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-cef6c0e8a8d22bfa` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T19:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-052:fact-06-fd317c06abed` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/1900Z - 20/2015Z |
| `cand-d26d0395dd1eb103` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-052:fact-01-2bb7c1d05c70` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD ELEMENT TYPE: APT |
| `cand-de018e8cba746389` | `S1_llm_only` | `'reports_new_maximum_delay_minutes'}` | {'class': 'delay_minutes_maximum', 'text': '73'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1939 / 73 / 48 |
| `cand-e167598435cdfdb3` | `S1_llm_only` | `'identifies_controlled_entity'}` | {'class': 'airport', 'text': 'IAD'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-e4fe9dbf3819f4bb` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-20T19:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-052:fact-04-70e593a6c163` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z DEP FACILITIES INCLUDED:... |
| `cand-e8e89e6e2c6b9638` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-7488de63f66152d8` | `fact-7488de63f66152d8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 201911-202115 SIGNATURE: 26/05/20 19:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-f131f9336da3a5e0` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-f7a74de532d39557` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-4e225078b5406aa3` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-fad05dd80044d277` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T19:11:00Z | `fact-ddaeeedb0c104e6a` | `fact-ddaeeedb0c104e6a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201911-202115 |

## ATCSCC-GOLD-057 / 2026-05-14:007

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=91, est=26 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 44
- Cross-system clusters: 43
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=7

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: FIRST TIER. EFFECTIVE TIME: 140030-140230 SIGNATURE: 26/05/14 00:31 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-cbb9d270f9f0ff36` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00ff70d7ec28296f` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-14T02:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140030-140230 |
| `cand-0779a10be34f8587` | `S1_llm_only` | `'has new maximum delay'}` | {'label': '62', 'type': 'delay_minutes_maximum'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-0beef83410f72a58` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | dca | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-057:fact-01-23148680ee41` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED:... |
| `cand-0cc999668a1216d1` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-14T00:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 140030-140230 |
| `cand-1b2b8007478f8279` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-14T02:30:00Z | `fact-2ebae9034de1357a` | `fact-2ebae9034de1357a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140030-140230 |
| `cand-1c14c9fbe3d94723` | `S2_llm_schema_slice` | `includesARTCC` | {'id': 'ZOB', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-201c7ed2bbca9dc9` | `S1_llm_only` | `'is impacted by'}` | {'label': 'WEATHER / THUNDERSTORMS', 'type': 'impacting_condition'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-261625e482afb014` | `S1_llm_only` | `'has new total delay'}` | {'label': '580', 'type': 'delay_minutes_total'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-2d6fee211ab5f847` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-312604950974ded1` | `S2_llm_schema_slice` | `controlledNASelement` | {'id': 'DCA', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-3745c37110055769` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 7 | `fact-7cb46936b468bc54` | `S1b_llm_canonicalized:2026-05-14:007:fact-38711ca7ffd2, fact-7cb46936b468bc54` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP |
| `cand-3754c9163126d92a` | `S2_llm_schema_slice` | `includesARTCC` | {'id': 'ZTL', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-394c345ea552693c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T00:31:00Z | `fact-ad817297e4e9e678` | `fact-ad817297e4e9e678` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 00:31 |
| `cand-3eac9bd85813aaab` | `S1_llm_only` | `'has ground stop period'}` | {'label': '13/2307Z - 14/0130Z', 'type': 'time_interval'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 13/2307Z - 14/0130Z |
| `cand-3f753ca7ff50d9ab` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-40a4ceea5c790b05` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-cbb9d270f9f0ff36` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-4127ed16bef6d5bb` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-4dc332b0d61eb4aa` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-057:fact-02-544bfbc4c5ac` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED:... |
| `cand-51ec07f4d6656a9d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-6ce3cc5cd6cfb123` | `fact-6ce3cc5cd6cfb123` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-530a420095cd4378` | `S1_llm_only` | `'announces ground stop for'}` | {'label': 'DCA', 'type': 'airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP |
| `cand-5770231af98ae5d2` | `S1_llm_only` | `'includes departure facilities'}` | {'label': 'ZTL ZDC ZNY ZJX ZOB ZBW ZID', 'type': 'facility_list'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-67fe35473cd9f772` | `S2_llm_schema_slice` | `includesARTCC` | {'id': 'ZNY', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-7a76c6773f4c0038` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `fact-16d35c26276132db` | `fact-16d35c26276132db` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA |
| `cand-83ec5b21411aa36e` | `S2_llm_schema_slice` | `includesARTCC` | {'id': 'ZJX', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-946db3f5a6d9541b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T00:30:00Z | `fact-c1afdb698ceb5642` | `fact-c1afdb698ceb5642` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 140030-140230 |
| `cand-9984cc71ae9ca7af` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-057:fact-03-d36b4c0a4f7e` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z DEP FACILITIES INCLUDED:... |
| `cand-9a0e96605ad50333` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-a13dfffc2c8c78dc` | `S1_llm_only` | `'has probability of extension'}` | {'label': 'MEDIUM', 'type': 'extension_probability'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a46d47c4b328854f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-c305edba23a6b994` | `fact-c305edba23a6b994` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a83b16a26f271365` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-a9003c7e001c8ce6` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-b6a7159e2fb74f0a` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T00:31:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/14 00:31 |
| `cand-bbe80583d729bcf6` | `S2_llm_schema_slice` | `departureScope` | {'id': '_:as1', 'type': 'atm:AirportSpec'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-bf18fc09b1e4a925` | `S2_llm_schema_slice` | `includesARTCC` | {'id': 'ZBW', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-c6957789d6a16e69` | `S1_llm_only` | `'has new average delay'}` | {'label': '36', 'type': 'delay_minutes_average'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 580 / 62 / 36 |
| `cand-cc3e3eca3fa5bda4` | `S1_llm_only` | `'has controlling element'}` | {'label': 'DCA', 'type': 'airport_element'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 0026Z GROUND STOP PERIOD: 13/2307Z - 14/0130Z |
| `cand-d5985bc576cac33f` | `S2_llm_schema_slice` | `advisoryNumber` | 7 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 007 |
| `cand-da4acd6904f05fc1` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-daa38ac4c981965f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-db01832d8feea916` | `S2_llm_schema_slice` | `includesARTCC` | {'id': 'ZDC', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-e7042b6bc82137ad` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-ed8c3debefc560ee` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | FIRST TIER. | `fact-c59ea57c65e7dc5f` | `fact-c59ea57c65e7dc5f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: FIRST TIER. |
| `cand-f55f5274abb97aa8` | `S2_llm_schema_slice` | `includesARTCC` | {'id': 'ZID', 'type': 'nas:ARTCC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-f68f674f945c0713` | `S2_llm_schema_slice` | `withinARTCC` | {'id': '_:tier1', 'type': 'nas:ARTCCtier'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |

## ATCSCC-GOLD-058 / 2026-05-20:139

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=91, est=26 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 44
- Cross-system clusters: 43
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=139

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DCA ELEMENT TYPE: APT ADL TIME: 2038Z GROUND STOP PERIOD: 20/2028Z - 20/2200Z CUMULATIVE PROGRAM PERIOD: 20/1930Z - 21/0359Z DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 571 / 129 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1722 / 148 / 78 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. EFFECTIVE TIME: 202042-202300 SIGNATURE: 26/05/20 20:43 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-68b038ed6c840adb` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-02bf0130c18d13eb` | `S1_llm_only` | `has_control_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-030021db1861f5a9` | `S1_llm_only` | `has_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-03a282e98b9d080b` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYHZ | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-53a9b12afe55` | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-08702035e1749c34` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-118c0524f5714ac6` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYUL | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-325a7bbbda77` | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-1e72958b2e6ea237` | `S1_llm_only` | `has_advisory_label` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-1e96c871d6ac6686` | `S1_llm_only` | `imposes_action` | GROUND STOP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP |
| `cand-1ff5ab6522b22585` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-20b945acb77bc242` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-2d9a6ae40fc3dcec` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-36d29eab0f505885` | `S1_llm_only` | `has_signature_timestamp` | 26/05/20 20:43 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 20:43 |
| `cand-3d41e07a1188e07c` | `S1_llm_only` | `has_ground_stop_period` | 20/2028Z - 20/2200Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2028Z - 20/2200Z |
| `cand-40eac1be7575b29f` | `S1_llm_only` | `has_advisory_time` | 2038Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2038Z |
| `cand-46829e1854575bdb` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYOW | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-ca3fd7b7b8de` | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-46e1d05072947f91` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-4b1269a8e91c5a6d` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-ac887ca8038621dc` | `S1b_llm_canonicalized:2026-05-20:139:fact-bcfe1e4b7526, S2_llm_schema_slice:ATCSCC-GOLD-058:fact-02-ffdc68edbeb2, fact-ac887ca8038621dc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-5193d25d038aada8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T23:00:00Z | `fact-716e7c2bca417886` | `fact-716e7c2bca417886` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202042-202300 |
| `cand-52dc10b385a7ae5b` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-546d1da359cb7c27` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T20:28:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-058:fact-06-d6fc7a941c83` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2028Z - 20/2200Z |
| `cand-6066104069ad1b82` | `S1_llm_only` | `states_comment` | LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. |
| `cand-610ed2a7437ae960` | `S1_llm_only` | `reports_previous_total_max_average_delays` | {'average': 26, 'maximum': 129, 'total': 571} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 571 / 129 / 26 |
| `cand-646042a866811a39` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T20:43:00Z | `fact-b2ee61d77e3926ff` | `S2_llm_schema_slice:ATCSCC-GOLD-058:fact-05-76b1f3bd0238, fact-b2ee61d77e3926ff` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/20 20:43 |
| `cand-6e743f3cb8b14751` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-68b038ed6c840adb` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6fc8e28c1c0ed16f` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `initiativeComments` | LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. | `fact-756c99942422a94a` | `S2_llm_schema_slice:ATCSCC-GOLD-058:fact-04-e290cbd8c0ac, fact-756c99942422a94a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | COMMENTS: LACK OF ROUTES DUE TO ENROUTE/TERMINAL T-STORMS IMPACTS. |
| `cand-72a6f6994ce61e9a` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYTZ | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-cdcacaa3cce6` | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-7d8c6984fc156d5c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADL | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-5c26e921d6ae` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-837b9bb5cfbb9dea` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-64cf0de8a7d27889` | `S2_llm_schema_slice:ATCSCC-GOLD-058:fact-03-89fcc95cb321, fact-64cf0de8a7d27889` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-868af18addebc2e5` | `S1_llm_only` | `has_cumulative_program_period` | 20/1930Z - 21/0359Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 20/1930Z - 21/0359Z |
| `cand-8b9a008c6fba7d60` | `S1_llm_only` | `includes_departure_facilities` | ['ZTL', 'ZDC', 'ZNY', 'ZJX', 'ZOB', 'ZBW', 'ZID', 'CYHZ', 'CYOW', 'CYUL', 'CYYZ', 'CYTZ', 'CYQB'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-8e1130e12511f33c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T20:42:00Z | `fact-0b82331470d22606` | `fact-0b82331470d22606` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202042-202300 |
| `cand-959ece441c86c0a3` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:APT | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-51ca05f6a7eb` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-9db174c408f3632a` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYQB | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-440f43adcd45` | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-9f69a54fc3cd2b4d` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport:DCA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-058:fact-01-5736f3438c71` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DCA ELEMENT TYPE: APT |
| `cand-a3899af16474b699` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 139 | `fact-a817e20bce9ad9c0` | `S1b_llm_canonicalized:2026-05-20:139:fact-b1f6f0ae935d, fact-a817e20bce9ad9c0` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-a64d3e442f381128` | `S1_llm_only` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a70b760eff016606` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-bdf494645b5c1019` | `S1_llm_only` | `has_effective_time` | 202042-202300 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202042-202300 |
| `cand-c0afd47375cf3aea` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-d5303e6517935a71` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CYYZ | `` | `S1b_llm_canonicalized:2026-05-20:139:fact-b4dd82207234` | `{"repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID CYHZ CYOW CYUL CYYZ CYTZ CYQB |
| `cand-e1adb58b994b1f66` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DCA | `fact-f6fcd2276ba719eb` | `S1b_llm_canonicalized:2026-05-20:139:fact-d61e3c040407, fact-f6fcd2276ba719eb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: DCA |
| `cand-e38414225995c1d1` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T22:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-058:fact-07-96883b0732ea` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2028Z - 20/2200Z |
| `cand-e8b9a3491d2ef251` | `S1_llm_only` | `reports_new_total_max_average_delays` | {'average': 78, 'maximum': 148, 'total': 1722} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1722 / 148 / 78 |
| `cand-ea0e1bed2d7eef53` | `S1_llm_only` | `targets_control_element` | DCA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DCA |
| `cand-ee006350b973bbfc` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-022 / 2026-05-15:064

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=89, est=25 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 43
- Cross-system clusters: 42
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=64

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1925Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z ANTICIPATED CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z ANTICIPATED PROGRAM RATE: 32 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1000 CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME ANTICIPATED MAXIMUM DELAY: 53 ANTICIPATED AVERAGE DELAY: 26 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z EFFECTIVE TIME: 151929-152059 SIGNATURE: 26/05/15 19:29 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Con...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-2381cff5585d7e70` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-094f22140ae44565` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-7c3a081eb55bcae8` | `fact-7c3a081eb55bcae8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-1635003ceb0b99ef` | `S1_llm_only` | `anticipated_cumulative_program_period` | 15/2200Z - 16/0029Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z |
| `cand-240145bc3abe741a` | `S2_llm_schema_slice` | `controlledNASelement` | nas:ARTCC/ZME | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-2de1380890b26b1b` | `S1_llm_only` | `advisory_time` | 1925Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 1925Z |
| `cand-3167af0fee031bf1` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport/BNA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-35fc5a5c1bfbe913` | `S1_llm_only` | `arrival_window_estimated_for` | 15/2200Z - 16/0029Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-428492ab62865bde` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport/BNA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-437e61390c681ba5` | `S1_llm_only` | `anticipated_program_rate` | 32 FLT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED PROGRAM RATE: 32 FLT |
| `cand-446273cac869270f` | `S1b_llm_canonicalized` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-4674b836ca5b672a` | `S1_llm_only` | `applies_to` | ZME | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-4a8e16e435b192b5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `fact-c0ee1dca6db0a55c` | `fact-c0ee1dca6db0a55c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-5610e99f038d001e` | `S1_llm_only` | `impacting_condition` | STAFFING | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-57ce8874d3627cb8` | `S1_llm_only` | `announces_ground_delay_program` | CDM PROPOSED GROUND DELAY PROGRAM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-5dcba8ac137fa961` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | other | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-022:fact-02-07642072cf63` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-67aa9cea399fd7f9` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-15T19:29:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/15 19:29 |
| `cand-6c6bfffe6f08d537` | `S0_rule_only` | `impactingCondition` | staffing | `fact-2381cff5585d7e70` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-6ebc8ed5e864e9bc` | `S1_llm_only` | `effective_time` | 151929-152059 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151929-152059 |
| `cand-6f2b09e40c5a60b5` | `S1_llm_only` | `anticipated_average_delay` | 26 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED AVERAGE DELAY: 26 |
| `cand-7002bfe91f58e99d` | `S2_llm_schema_slice` | `impactingConditionMessage` | STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-7129bee378c8832a` | `S1_llm_only` | `element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-73e4a36d8cfbecf6` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-15T20:59:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151929-152059 |
| `cand-781b0734f521568c` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-15T19:25:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1925Z |
| `cand-7bd1da295e8146b4` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:NONE | `` | `S1b_llm_canonicalized:2026-05-15:064:fact-f1cb32e0390a` | `{"repaired_accepted": 1}` | `{}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-879036b514440ee8` | `S1_llm_only` | `canadian_departure_airports_included` | NONE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-87af7a67a8da3c09` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T19:29:00Z | `fact-1351a6c33904a819` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-022:fact-03-c909827de737, fact-1351a6c33904a819` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/15 19:29 |
| `cand-8adc4b2b880e8374` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 64 | `fact-55b0d42ff2fa3295` | `S1b_llm_canonicalized:2026-05-15:064:fact-4ce3b4ff1a10, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-022:fact-04-c3c5ce9ef76d, fact-55b0d42ff2fa3295` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-8d11aae1aaf9f22d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T19:29:00Z | `fact-905e6d91591765ec` | `fact-905e6d91591765ec` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151929-152059 |
| `cand-95c98040b6999169` | `S1_llm_only` | `staffing_comment` | PROPOSAL ONLY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: PROPOSAL ONLY. |
| `cand-9ad275f55840f42f` | `S2_llm_schema_slice` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-9b238f9c0e5fec81` | `S1_llm_only` | `must_be_received_by` | 15/2000Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-a9351ea9d710cf21` | `S2_llm_schema_slice` | `type` | atm:GroundDelayProgramTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-b31e727ee7d4e74f` | `S2_llm_schema_slice` | `departureScope` | {'atm:includesAirport': 'all contiguous US departure airports', 'type': 'atm:AirportSpec'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-cb27d7fb0cbc0dbf` | `S1_llm_only` | `controlled_terminal_element` | BNA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-d0e000c7a1c4e78c` | `S2_llm_schema_slice` | `departureScope` | {'atm:includesAirport': 'BNA', 'type': 'atm:AirportSpec'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-d226ad7515cb8c44` | `S2_llm_schema_slice` | `flightInclusionSpec` | {'description': 'ALL CONTIGUOUS US DEP', 'type': 'atm:FlightSpec'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-d523ea5609a93884` | `S2_llm_schema_slice` | `advisoryNumber` | 64 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `cand-dae06c910c0e4dcf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z | `fact-81736a81f66cfa32` | `fact-81736a81f66cfa32` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: PROPOSAL ONLY. CONFERENCE AT 1945Z USER UPDATES MUST BE RECEIVED BY: 15/2000Z |
| `cand-dc95c96f77321922` | `S1_llm_only` | `anticipated_maximum_delay` | 53 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ANTICIPATED MAXIMUM DELAY: 53 |
| `cand-e664f8d2945ed5ea` | `S1_llm_only` | `conference_time` | 1945Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONFERENCE AT 1945Z |
| `cand-ec8e76da4d160024` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | nas:Airport(BNA) | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-022:fact-01-29c403e77982` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT |
| `cand-efc7af5809f60e79` | `S1_llm_only` | `delay_assignment_mode` | UDP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-f3d1f2325bb196fa` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T20:59:00Z | `fact-1c0251818d7d2f1f` | `fact-1c0251818d7d2f1f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151929-152059 |
| `cand-f541b536ee9bd87f` | `S1_llm_only` | `applies_to_scope` | ALL CONTIGUOUS US DEP | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_object_class": 1, "unknown_predicate": 1, "unknown_s...` | INCL: ALL CONTIGUOUS US DEP SCOPE: 1000 |

## ATCSCC-GOLD-054 / 2026-05-20:153

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=89, est=25 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 43
- Cross-system clusters: 42
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=153

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 628 / 65 / 25 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1584 / 110 / 63 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: GROUN STOP EXTENDED. EFFECTIVE TIME: 202130-202315 SIGNATURE: 26/05/20 21:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-7291476bb9233bef` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08a65876752aa03d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-09e1bc8e4722fe12` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-7291476bb9233bef` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-0f2d122ab727c7a1` | `S3_llm_schema_slice_validator_repair` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1049fcb21b3b9032` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-14062b552798e281` | `S2_llm_schema_slice` | `initiativeComments` | GROUN STOP EXTENDED. | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-18ac61f190056366` | `S1_llm_only` | `'reports previous total maximum average delays'}` | {'class': 'delay_statistics', 'text': '628 / 65 / 25'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 628 / 65 / 25 |
| `cand-1a45287aa0a9318a` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2f54036d68ec37ae` | `S1_llm_only` | `'states probability of extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-3275ddb90364c26b` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-337a2d76c001565b` | `S2_llm_schema_slice` | `controlledNASelement` | BWI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-054:fact-01-bd9d6bd629f7` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-37186d5ecb5a3b08` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-41d11745669b90df` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-20T21:14:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-473b8b413578613a` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-47a0adf6ab4bbfeb` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-52469d069237dd82` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-cfe592c7a5e88224` | `S1b_llm_canonicalized:2026-05-20:153:fact-bcfe1e4b7526, fact-cfe592c7a5e88224` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-52669e100b827362` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T21:24:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-57b72cffed9a358a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T21:30:00Z | `fact-d47612f844f3307b` | `fact-d47612f844f3307b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 21:30 |
| `cand-5c0d996953035406` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-63bc22bfda199f46` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T22:15:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-685e4dfa567b5161` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BWI | `fact-95fb1f6ed4c62f23` | `S1b_llm_canonicalized:2026-05-20:153:fact-c95ee14670ea, fact-95fb1f6ed4c62f23` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: BWI |
| `cand-6b32876d6bf95a7f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-6ca759ee111517d3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T23:15:00Z | `fact-8744c1f58b6c527f` | `fact-8744c1f58b6c527f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202130-202315 |
| `cand-6d41286bcf36f186` | `S1_llm_only` | `'notes comment about ground stop extension'}` | {'class': 'comment_statement', 'text': 'GROUN STOP EXTENDED.'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-7a2add7a6f4eb443` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-20T22:15:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-856015722c03e343` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-05cdbb338db405dc` | `fact-05cdbb338db405dc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8f5ee492b39ece79` | `S1_llm_only` | `'states advisory type'}` | {'class': 'ground_stop_advisory', 'text': 'CDM GROUND STOP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-a45d243ecf475214` | `S1_llm_only` | `'declares ground stop period'}` | {'class': 'time_interval', 'text': '20/2114Z - 20/2215Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-aaf422efb6dda6d0` | `S1_llm_only` | `'gives effective time window'}` | {'class': 'effective_time_interval', 'text': '202130-202315'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202130-202315 |
| `cand-ac660c2f029ddeae` | `S1_llm_only` | `'reports new total maximum average delays'}` | {'class': 'delay_statistics', 'text': '1584 / 110 / 63'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1584 / 110 / 63 |
| `cand-b41e7b984bed4b5a` | `S1_llm_only` | `'includes departure facilities'}` | {'class': 'facility_group', 'text': 'ZTL ZDC ZNY ZJX ZOB ZBW ZID'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-be2cea68b0170f53` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 153 | `fact-aa70227631cfd053` | `S1b_llm_canonicalized:2026-05-20:153:fact-311e47f57bb0, fact-aa70227631cfd053` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-c7f85d52bf2a1422` | `S2_llm_schema_slice` | `advisoryNumber` | 153 | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-cc7872e5ad5b3b3b` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T21:14:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-cd2e9aef6a226797` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'label': 'BWI', 'type': 'nas:Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BWI ELEMENT TYPE: APT ADL TIME: 2124Z GROUND STOP PERIOD: 20/2114Z - 20/2215Z |
| `cand-d018f0928bcdd626` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | GROUN STOP EXTENDED. | `fact-21b094a1980785a0` | `fact-21b094a1980785a0` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-d2d865108d1eb96b` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | GROUN STOP EXTENDED. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: GROUN STOP EXTENDED. |
| `cand-d3f89ec9f97594a5` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-dec86b0483509ab6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T21:30:00Z | `fact-23efe24e2664144d` | `fact-23efe24e2664144d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202130-202315 |
| `cand-df55753fa2614c16` | `S1_llm_only` | `'lists impacting condition'}` | {'class': 'impacting_condition', 'text': 'WEATHER / THUNDERSTORMS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e17190612808c41f` | `S3_llm_schema_slice_validator_repair` | `type` | atm:GroundStopTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-ec3318af48c1ae8d` | `S1_llm_only` | `'identifies control element'}` | {'class': 'airport_control_element', 'text': 'BWI'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BWI |
| `cand-f5326bc59e36a734` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-f6008ad9b48d3967` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-20T21:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 21:30 |

## ATCSCC-GOLD-027 / 2026-05-19:110

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=87, est=25 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 42
- Cross-system clusters: 41
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=110

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 125 / 43 / 42 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. EFFECTIVE TIME: 192111-192245 SIGNATURE: 26/05/19 21:12 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-759cc1b096d2dada` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-041db9b70938f3b1` | `S1_llm_only` | `has ground stop period` | 19/2058Z - 19/2145Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DEL... |
| `cand-1a8aeb85505b7f96` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T20:58:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-027:fact-03-ab683a8031c0` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-21ee2bd00955d6ba` | `S1_llm_only` | `has advisory time` | 2108Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DEL... |
| `cand-34a6658fac5f4e71` | `S1_llm_only` | `has element type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DEL... |
| `cand-3c4a3bc5521a93f6` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `fact-fd3da764b14c378e` | `fact-fd3da764b14c378e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. |
| `cand-4858ddc04ced51eb` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `` | `S1b_llm_canonicalized:2026-05-19:110:fact-95fad2fdb2f2` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DEL... |
| `cand-4b41f8839fa69951` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T21:08:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-027:fact-02-82afc174458f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-4bb5041e4267edc7` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-19T21:45:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-027:fact-04-bf4cc6c237a1` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-5004e9f39e3dcaa2` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T21:12:00Z | `fact-74faffb462a9405a` | `fact-74faffb462a9405a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 21:12 |
| `cand-5029b30861d97c10` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 110 | `fact-f65005383ac1cd9b` | `S1b_llm_canonicalized:2026-05-19:110:fact-43be5e4205b1, fact-f65005383ac1cd9b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP |
| `cand-554b998aa5ea9cd6` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID |
| `cand-5623e511d654b4e4` | `S1_llm_only` | `notes comment` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. |
| `cand-5a860d397a62a131` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID |
| `cand-60776eb97d5a0e71` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T22:45:00Z | `fact-c7e975ab7c1cd57f` | `fact-c7e975ab7c1cd57f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192111-192245 |
| `cand-6cfa818bd4ce0bad` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-180b29d904e93ac2` | `S1b_llm_canonicalized:2026-05-19:110:fact-bcfe1e4b7526, fact-180b29d904e93ac2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-6f54610c2dc99d3f` | `S2_llm_schema_slice` | `controlledNASelement` | ORD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-027:fact-07-a200e240df53` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-7afbb9bd387419a3` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-19T20:58:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-027:fact-05-d38d4af17568` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-7c92f4064c779310` | `S1_llm_only` | `reports previous delays` | 0 / 0 / 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-887769b4dc25b79d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-24f7509f27894208` | `fact-24f7509f27894208` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-889e5f1856abda3a` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID |
| `cand-8df6484f32742834` | `S1_llm_only` | `reports new delays` | 125 / 43 / 42 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 125 / 43 / 42 |
| `cand-961c7fb697a7950c` | `S1b_llm_canonicalized` | `advisoryNumber` | 110 | `` | `S1b_llm_canonicalized:2026-05-19:110:fact-25f1c65a532b` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DEL... |
| `cand-9735ee3aa76335f2` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-9d3794e899b6dcdf` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-759cc1b096d2dada` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-a087e7b44bbbea77` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID |
| `cand-a4a0095be74fb497` | `S1_llm_only` | `states probability of extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a7f6f447b9393f68` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T21:11:00Z | `fact-6fdb7a451dab76e2` | `fact-6fdb7a451dab76e2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 192111-192245 |
| `cand-a986c3ddcebfa716` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-027:fact-02-2851bf85b088` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-b57bd7640bc45c8d` | `S1_llm_only` | `includes departure facilities` | ZDC ZNY ZOB ZID | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID |
| `cand-b6ea5d2cbbac9287` | `S3_llm_schema_slice_validator_repair` | `impactingCondition` | weather | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-027:fact-03-81a6438977d7` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-b89038b717fd3e0a` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-19T21:45:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-027:fact-06-6fee7a09b990` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-be88a1245d080104` | `S1b_llm_canonicalized` | `advisoryNumber` | 110 | `` | `S1b_llm_canonicalized:2026-05-19:110:fact-92cdba25b29e` | `{"repaired_accepted": 1}` | `{}` | COMMENTS: ZBW RELEASED. ADVZY 105 IN EFFECT. |
| `cand-c2805ce52554d96a` | `S2_llm_schema_slice` | `advisoryNumber` | 110 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-027:fact-01-317702c8470c` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-d15659d15eee663d` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `S2_llm_schema_slice:ATCSCC-GOLD-027:fact-05-75ddbb6770e4` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-d2ff6eaee5492cb6` | `S1_llm_only` | `names control element` | ORD ELEMENT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED: (Manual) ZDC ZNY ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DEL... |
| `cand-d62e8b14d87ca294` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `fact-93a08de6f760332a` | `fact-93a08de6f760332a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD |
| `cand-d7700b5fb977b9c5` | `S1_llm_only` | `has advisory headline` | ORD/ZAU 05/19/2026 CDM GROUND STOP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP |
| `cand-e07959f6c4bcb619` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | {"evidence_text": "CTL ELEMENT: ORD ELEMENT TYPE: APT", "type": "nas:Airport"} | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-027:fact-01-3bc9a2f046b8` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT |
| `cand-e0cc34cea7cbb4c2` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | ZBW RELEASED. ADVZY 105 IN EFFECT. | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-027:fact-04-955f2266ee14` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |
| `cand-ee82375348b0458c` | `S1_llm_only` | `names impacting condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-f752b6e5b95bfe00` | `S1_llm_only` | `has effective time window` | 192111-192245 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 192111-192245 |
| `cand-fe84afe7933e42e9` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `S2_llm_schema_slice:ATCSCC-GOLD-027:fact-06-36793fce0995` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 2108Z GROUND STOP PERIOD: 19/2058Z - 19/2145Z DEP FACILITIES INCLUDED:... |

## ATCSCC-GOLD-012 / 2026-05-18:053

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=86, est=25 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 41
- Cross-system clusters: 41
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=53

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL MESSAGE: NAME: ATL_NO_JJEDI_PARTIAL CONSTRAINED AREA: ZTL REASON: EQUIPMENT INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 181400 TO 181800 PROBABILITY OF EXTENSION: MODERATE REMARKS: ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KJAX KATL >QUIWE LEAVI < OZZZI2 KMYR KSAV KSSI KEWN KFAY KILM KATL >RDU SHPRD LEAVI < OZZZI2 KOAJ KORF KPHF KRDU ZJX(-CAE -CHS -JAX KATL >AMORY Q110 DAWWN BEORN < -MYR -SAV -SSI) HOBTT3 ZMA KATL >AMORY Q110 DAWWN BEORN < HOBTT3 TMI ID: RRDCC502 EFFECTIVE TI...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-684f702cb73c4f05` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-003b8abf4289bd3f` | `S1_llm_only` | `valid_during` | ETD 181400 TO 181800 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 181400 TO 181800 |
| `cand-0e4205d1807be52a` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T14:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181400-181800 |
| `cand-22a16c355041ac38` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-270c2629199be2a6` | `S0_rule_only, S1b_llm_canonicalized` | `extensionProbability` | MODERATE | `fact-684f702cb73c4f05` | `` | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-2bd0573eba3c10c6` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL |
| `cand-350890bc37a331a2` | `S1_llm_only` | `includes_traffic` | ['KCAE', 'KCHS', 'KEWN', 'KFAY', 'KILM', 'KJAX', 'KMYR', 'KOAJ', 'KORF', 'KPHF', 'KRDU', 'KSAV', 'KSSI', 'ZJX', 'ZMA'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA |
| `cand-3923a6377a4387a0` | `S1_llm_only` | `has_probability_of_extension` | MODERATE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-398e4fcf7bd8ebb5` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-18T13:52:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-06-39c1057fc30d` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 13:52 |
| `cand-3f9fd1e7a1abe1c3` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-414322a726e66bcc` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-01-26667ee97cce` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-5a971da768e91731` | `S2_llm_schema_slice` | `controlledNASelement` | KATL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL |
| `cand-5f94bc7b02e0a4e5` | `S2_llm_schema_slice` | `advisoryNumber` | 53 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-611f453f8404c7ae` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL |
| `cand-62a8f2302b149c21` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-04-d34047ce7114` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | VALID: ETD 181400 TO 181800 PROBABILITY OF EXTENSION: MODERATE |
| `cand-659c1966ce58777e` | `S1_llm_only` | `has_effective_time` | 181400-181800 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181400-181800 |
| `cand-7015c5ce41f8fd11` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteType` | ROUTE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-02-4c1fda0fb603` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-7247e89ec08e122b` | `S1_llm_only` | `has_tmi_id` | RRDCC502 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC502 |
| `cand-7cf87ccc59cd8965` | `S1_llm_only` | `includes_departures_to` | KATL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL |
| `cand-7d076ccedd6551a4` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteReason` | EQUIPMENT | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-03-aba78359b0d4` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | NAME: ATL_NO_JJEDI_PARTIAL CONSTRAINED AREA: ZTL REASON: EQUIPMENT INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL... |
| `cand-7e09e2ead1851f3b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T14:00:00Z | `fact-969bdf5c8913bf99` | `fact-969bdf5c8913bf99` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181400-181800 |
| `cand-8099730e3b0aa728` | `S1_llm_only` | `is_named` | ATCSCC advisory traffic route restriction | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: ATL_NO_JJEDI_PARTIAL |
| `cand-80eda471e39fa04f` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T18:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181400-181800 |
| `cand-870e604de607b700` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T13:52:00Z | `fact-fcb97a186c8d5da8` | `fact-fcb97a186c8d5da8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 13:52 |
| `cand-89cf7870a7c3196d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 53 | `fact-29a644ad60f42e6e` | `fact-29a644ad60f42e6e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-8d79adff49473afb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T18:00:00Z | `fact-9e96b2053e1dea94` | `fact-9e96b2053e1dea94` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181400-181800 |
| `cand-8f2907b301b015fb` | `S1_llm_only` | `modifies_routes_for_origin_destination` | [{'destination': 'KATL', 'origin': 'KCAE', 'route': 'QUIWE LEAVI'}, {'destination': 'KATL', 'origin': 'KCHS', 'route': 'QUIWE LEAVI'}, {'... | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ROUTES: ORIG DEST ROUTE ---- ---- ----- KCAE KCHS KJAX KATL >QUIWE LEAVI < OZZZI2 KMYR KSAV KSSI KEWN KFAY KILM KATL >RDU SHPRD LEAVI < OZZZI2 KOAJ KORF KPHF KRDU ZJX(-CAE -CHS... |
| `cand-988a69dafdaa3c82` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T13:52:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 13:52 |
| `cand-993b34417a8c0a44` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL |
| `cand-a5b1ca988a90df7f` | `S1_llm_only` | `applies_flight_status` | ALL_FLIGHTS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-b40fe8b8c7a07b12` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:KATL | `` | `S1b_llm_canonicalized:2026-05-18:053:fact-e159a0485ecc` | `{"repaired_accepted": 1}` | `{}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL |
| `cand-be68ee8ce1be25d2` | `S1_llm_only` | `has_facilities_included` | ['ZDC', 'ZJX', 'ZMA', 'ZTL'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL |
| `cand-bfe3a5ee948cd340` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | KATL | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-05-c7236f5548ae` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES TO KATL |
| `cand-d55c58157dfe4827` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-18T18:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-08-effd0f34a492` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181400-181800 |
| `cand-d7d335097c3e1d8b` | `S1_llm_only` | `has_reason` | equipment | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: EQUIPMENT |
| `cand-ddfd0269b3d72384` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `cand-de33183135dbd189` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZDC/ZJX/ZMA/ZTL |
| `cand-e53da0ec312fb38b` | `S1b_llm_canonicalized` | `impactingCondition` | equipment | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: EQUIPMENT |
| `cand-ea27b0288a8be80b` | `S1_llm_only` | `has_constrained_area` | ZTL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZTL |
| `cand-ef6a8c9e74f87d66` | `S2_llm_schema_slice` | `reRouteReason` | EQUIPMENT | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | REASON: EQUIPMENT |
| `cand-f7b70b6c53c0bc1f` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | NAME: ATL_NO_JJEDI_PARTIAL CONSTRAINED AREA: ZTL REASON: EQUIPMENT INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K R... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-09-e42be4d3eada` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: ATL_NO_JJEDI_PARTIAL CONSTRAINED AREA: ZTL REASON: EQUIPMENT INCLUDE TRAFFIC: KCAE/KCHS/KEWN/KFAY/KILM/KJAX/KMYR/KOAJ/KORF/KPHF/K RDU/KSAV/KSSI/ZJX/ZMA DEPARTURES... |
| `cand-fd5ac50b27fa1adc` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-18T14:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-012:fact-07-1f9e19ef81c9` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181400-181800 |

## ATCSCC-GOLD-026 / 2026-05-18:055

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=83, est=24 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 40
- Cross-system clusters: 39
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=55

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 467 / 84 / 52 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-4d777d2245a650f2` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-034db367e9d375fd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T14:13:00Z | `fact-13b1a33e157b5b61` | `fact-13b1a33e157b5b61` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181413-181630 |
| `cand-083e3ed6eff857ca` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-18T14:01:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-0c0cceff9e74d754` | `S1_llm_only` | `has_ground_stop_period` | 18/1401Z - 18/1530Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-1119e9bba0d1f7b6` | `S1_llm_only` | `has_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-126a8e3c5e6277a6` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-1278acf0f5f15423` | `S1_llm_only` | `has_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-147a3a2134b37878` | `S1_llm_only` | `has_signature_timestamp` | 26/05/18 14:13 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 14:13 |
| `cand-19b4144d49456889` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-4d777d2245a650f2` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-2232b3e06191c950` | `S2_llm_schema_slice` | `advisoryNumber` | 55 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-2c12a9dca07ddad4` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-2f064ad5f77b7020` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-324b120137d8a604` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `fact-78d4483076037fc3` | `fact-78d4483076037fc3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL |
| `cand-32c296f073cc8bda` | `S1_llm_only` | `has_advisory_time` | 1411Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-341e0851e7b7cd80` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `` | `S1b_llm_canonicalized:2026-05-18:055:fact-612bc35421f0` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-3bca2d20bb94f614` | `S1_llm_only` | `has_new_total_maximum_average_delays` | 467 / 84 / 52 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 467 / 84 / 52 |
| `cand-4b4e37c2fc8fd5a1` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | nas:Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT |
| `cand-4bd475d0799bc7bc` | `S1_llm_only` | `has_effective_time` | 181413-181630 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181413-181630 |
| `cand-51b520b4b1a90fc5` | `S3_llm_schema_slice_validator_repair` | `type` | atm:GroundStopTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-5382f4d04112c735` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-580e03d4bcef1cab` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-5b35dc0ac59a8d20` | `S1_llm_only` | `has_advisory_identifier` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-664d400a1c932b83` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-b5a5e941b7d06f95` | `fact-b5a5e941b7d06f95` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6771a5c6cbe85cd9` | `S1_llm_only` | `specifies_control_element` | STL ELEMENT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 1411Z GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-6791d9de3452d8c9` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-6e469dea97c7729e` | `S1_llm_only` | `has_previous_total_maximum_average_delays` | 0 / 0 / 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-8bbdaeff5c0419d2` | `S2_llm_schema_slice` | `initiativeComments` | EFFECTIVE TIME: 181413-181630 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181413-181630 |
| `cand-90d0e1d5258bb093` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-18T14:13:00Z | `` | `` | `{"rejected_schema": 2}` | `{"predicate_not_object_property": 2, "unknown_object_class": 2, "unknown_subject_class": 2}` | SIGNATURE: 26/05/18 14:13 |
| `cand-a64f6810243d3806` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T16:30:00Z | `fact-119a940e3067ec59` | `fact-119a940e3067ec59` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181413-181630 |
| `cand-a9218208bf740473` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-aaceefc344aa46c5` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 55 | `fact-8a2adda36cdb22f0` | `S1b_llm_canonicalized:2026-05-18:055:fact-a47dc9f8abfa, fact-8a2adda36cdb22f0` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-ac9a128f0ab1b7f9` | `S1_llm_only` | `is_impacted_by_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b2eb6cfea87c9b49` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-18T15:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1401Z - 18/1530Z |
| `cand-b77fac0eec6e5fcb` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-baa86ee95e78679d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-d04e443507f84da8` | `fact-d04e443507f84da8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 181413-181630 SIGNATURE: 26/05/18 14:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-bad733d9987e2833` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-bc1b6c4b8e2dbfe3` | `S1_llm_only` | `includes_departure_facilities` | ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-d39d265249a67f2d` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-b3e8a2b07ed71057` | `S1b_llm_canonicalized:2026-05-18:055:fact-bcfe1e4b7526, fact-b3e8a2b07ed71057` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-df8069f61bcb616f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T14:13:00Z | `fact-6502a20e8a2135f6` | `fact-6502a20e8a2135f6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 14:13 |
| `cand-dfcac868e20bf43b` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |
| `cand-f109bc903470d414` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZAU ZFW ZDV ZKC ZME ZID ZAB ZMP |

## ATCSCC-GOLD-013 / 2026-05-18:124

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=82, est=24 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 39
- Cross-system clusters: 39
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=124

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD MESSAGE: NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 182000 TO 190000 PROBABILITY OF EXTENSION: MODERATE REMARKS: REPLACES ADVZY 104. AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ZTL ADDED ROUTES: ORIG DEST ROUTE ---- ---- ----- ZTL KORD >VLKNN MEMFS RZC BUM IRK < BENKY6 KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK < KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK < BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK < BENKY6 ZME KORD >MEMFS RZC BUM IRK < B...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-6d2f6d418f369ec3` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05e0b2973029e073` | `S1_llm_only` | `has_reason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-12b78efa1a699ca3` | `S1_llm_only` | `includes_traffic` | KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-16bb5ccf18c4b1f8` | `S1_llm_only` | `has_flight_status` | ALL_FLIGHTS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-1f33effa579b2350` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-21f118f3a5b2152e` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | nas:Airport KORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KCAE/KCHS/KJAX/KSAV/ZJX/ZMA/ZME DEPARTURES TO KORD |
| `cand-26689bb885e41e7b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T20:00:00Z | `fact-1dc8154638589cdd` | `fact-1dc8154638589cdd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-29a8eb9326a897a2` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-18T18:20:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-37239a3cf62010ba` | `S1_llm_only` | `valid_during` | ETD 182000 TO 190000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-3972153221e203a7` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-45349db3b3c7d54c` | `S1_llm_only` | `contains_route` | ZME KORD >MEMFS RZC BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZME KORD >MEMFS RZC BUM IRK |
| `cand-4592d1761705bd89` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-4c1d36bb9ec5ffe6` | `S0_rule_only, S1b_llm_canonicalized` | `extensionProbability` | MODERATE | `fact-6d2f6d418f369ec3` | `` | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-533db2df650415e1` | `S1_llm_only` | `has_advisory_name` | SOUTHEAST_TO_ORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: SOUTHEAST_TO_ORD |
| `cand-5daa50298b383bed` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-18T19:00:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | VALID: ETD 182000 TO 190000 |
| `cand-61f47fd03c17679c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-716aca1928030247` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T00:00:00Z | `fact-a46f23eeee44e013` | `fact-a46f23eeee44e013` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182000-190000 |
| `cand-74cff1c68515c832` | `S3_llm_schema_slice_validator_repair` | `implementationStatus` | RQD | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-7ff1c70b0477735a` | `S1_llm_only` | `has_associated_restrictions` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AD-HOC ROUTING ASSOCIATED RESTRICTIONS: |
| `cand-825f2d53a3f25025` | `S1_llm_only` | `contains_route` | ZTL KORD >VLKNN MEMFS RZC BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZTL KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-8275574b77ed8b10` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-8321162e978d53be` | `S1_llm_only` | `contains_route` | ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 ZMA KORD >JAWJA Q116 VLKNN MEMFS RZC BUM IRK |
| `cand-8a1e80337beca404` | `S1_llm_only` | `lists_facilities_included` | ZAU/ZJX/ZKC/ZMA/ZME/ZTL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-8b3cc44e4fe9a6ba` | `S1b_llm_canonicalized` | `advisoryNumber` | 124 | `` | `S1b_llm_canonicalized:2026-05-18:124:fact-a2de4721847a` | `{"repaired_accepted": 1}` | `{}` | REPLACES ADVZY 104. |
| `cand-8c0f3c8b840a1f6f` | `S3_llm_schema_slice_validator_repair` | `reRouteType` | ROUTE | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-93b7510e06d10236` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 124 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-9571431ac4e15cc9` | `S1_llm_only` | `contains_route` | KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KJAX BENKY6 ZJX(-CAE -CHS -JAX KORD >JAWJA Q116 VLKNN MEMFS RZC -SAV) BUM IRK |
| `cand-95f6f1d59aff6f4e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |
| `cand-96ea8fb8f51a18c3` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T20:25:00Z | `fact-3d1814a047f43698` | `fact-3d1814a047f43698` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:25 |
| `cand-a892c4767a7a5125` | `S1_llm_only` | `replaces_advisory` | ADVZY 104 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REPLACES ADVZY 104. |
| `cand-bc342f521179407e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 124 | `fact-490e2645e3b2d770` | `fact-490e2645e3b2d770` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `cand-c296dfa9e75b6722` | `S1_llm_only` | `has_probability_of_extension` | MODERATE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-c8f579df8378bb3f` | `S3_llm_schema_slice_validator_repair` | `reRouteReason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | NAME: SOUTHEAST_TO_ORD CONSTRAINED AREA: ZID/ZOB REASON: WEATHER |
| `cand-ccb396b245e43990` | `S1_llm_only` | `has_constrained_area` | ZID/ZOB | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZID/ZOB |
| `cand-d1c37fa13f9e18a9` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-18T20:25:00 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |
| `cand-d62e5c683bdc1e1e` | `S1_llm_only` | `notes_modification` | ZTL ADDED ROUTES | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: ZTL ADDED ROUTES: |
| `cand-e04af36f322e3e98` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-e4879f009a1b2bb6` | `S1_llm_only` | `contains_route` | KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | BENKY6 KCAE KCHS KSAV KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-f69a8f7a0893b27b` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | REPLACES ADVZY 104. AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ZTL ADDED ROUTES: ORIG DEST ROUTE ---- ---- ----- ZTL KORD >VL... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 104. AD-HOC ROUTING ASSOCIATED RESTRICTIONS: MODIFICATIONS: ZTL ADDED ROUTES: ORIG DEST ROUTE ---- ---- ----- ZTL KORD >VLKNN MEMFS RZC BUM IRK |
| `cand-f957732924f8d1b0` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZAU/ZJX/ZKC/ZMA/ZME/ZTL |

## ATCSCC-GOLD-019 / 2026-05-15:067

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=81, est=24 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 39
- Cross-system clusters: 38
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=67

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1945Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z PROGRAM RATE: 32 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: 1000 CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME MAXIMUM DELAY: 59 AVERAGE DELAY: 29 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 EFFECTIVE TIME: 151949-160129 SIGNATURE: 26/05/15 19:50 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-e266b922c1167993` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0bb5d003c0d4469b` | `S1_llm_only` | `declares_advisory_type` | APT ADL TIME | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL TIME: 1945Z |
| `cand-167b09511325cd40` | `S2_llm_schema_slice` | `includesAirportType` | contiguous us dep | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-1bc2930f7fc181b7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 | `fact-d005cfb8728605d1` | `fact-d005cfb8728605d1` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-25531eeaeeba0703` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-019:fact-07-1f5cbe8efc47` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-25dfffffa896cb19` | `S1b_llm_canonicalized` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-2a02c3637fcc4eb9` | `S1_llm_only` | `states_cumulative_program_period` | 15/2200Z - 16/0029Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 15/2200Z - 16/0029Z |
| `cand-31776c8923d37881` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-16T01:29:00Z | `fact-132c3221a0fcc5f1` | `fact-132c3221a0fcc5f1` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151949-160129 |
| `cand-33b0bf03ca891c29` | `S1_llm_only` | `defines_flight_inclusion_scope` | ALL CONTIGUOUS US DEP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-377dfbae807ae58a` | `S1_llm_only` | `states_impacting_condition` | STAFFING | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-38515591a586af99` | `S1_llm_only` | `states_average_delay` | 29 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 29 |
| `cand-493af27efc79c7d4` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | nas:Airport | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-019:fact-01-62f3badedc52` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT |
| `cand-596cf025b83a0882` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-15T22:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-019:fact-05-71834e681c42` | `{"repaired_accepted": 1}` | `{}` | ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-5c119a1fe8c8d670` | `S2_llm_schema_slice` | `controlledNASelement` | BNA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1945Z |
| `cand-619f6bd7935dd3a4` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-16T00:29:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-019:fact-06-149d1caa5751` | `{"repaired_accepted": 1}` | `{}` | ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-79437fc413bb62be` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 67 | `fact-8df26e4779586972` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-019:fact-03-2058471fa74a, fact-8df26e4779586972` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-7c77732637f53389` | `S2_llm_schema_slice` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-7dcc81fc74884ebd` | `S2_llm_schema_slice` | `advisoryNumber` | 67 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-808d4dd6b9ed5ad1` | `S1_llm_only` | `states_effective_time` | 151949-160129 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 151949-160129 |
| `cand-8827eb9ac7931c9e` | `S1_llm_only` | `sets_delay_assignment_mode` | UDP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-943506a59f6331c2` | `S1_llm_only` | `sets_program_rate` | 32 FLT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 32 FLT |
| `cand-97281e6398671c46` | `S1_llm_only` | `defines_departure_scope` | 1000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: 1000 |
| `cand-9be572fdf0d7eca1` | `S2_llm_schema_slice` | `departureScope` | _:airportSpec1 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP |
| `cand-9c340ca92c523055` | `S1_llm_only` | `states_canadian_departure_airports_included` | NONE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-9f732ebf95cf78e1` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:NONE | `` | `S1b_llm_canonicalized:2026-05-15:067:fact-f1cb32e0390a` | `{"repaired_accepted": 1}` | `{}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-b318df9913a787f7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | other | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-019:fact-02-08a6b1af1615` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-be4552892c347273` | `S0_rule_only` | `impactingCondition` | staffing | `fact-e266b922c1167993` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-c20771ecfb1b18b6` | `S1_llm_only` | `includes_staffing_comments` | ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | STAFFING COMMENTS: ARR 20L, DEP 20R, ZERO POP UP, EXEMPT TIME +45 |
| `cand-ca996534e7f48177` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-16T00:29:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-cc845a160df7a9e2` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `fact-8d000b416064261b` | `S1b_llm_canonicalized:2026-05-15:067:fact-89c012fad318, fact-8d000b416064261b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: BNA |
| `cand-cd264f9cbb1149da` | `S1_llm_only` | `applies_delay_assignment_table_to` | ZME | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-ce2bacbf99b6f3e4` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T19:50:00Z | `fact-e574a655c78d226d` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-019:fact-04-9a0847543cc8, fact-e574a655c78d226d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/15 19:50 |
| `cand-d879285cebae94ef` | `S2_llm_schema_slice` | `includesAirport` | CANADIAN DEP ARPTS INCLUDED: NONE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-dc94b80e04a7fb38` | `S1_llm_only` | `states_maximum_delay` | 59 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 59 |
| `cand-e0910e5d97943bf4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T19:49:00Z | `fact-90a1d0fefa8cc563` | `fact-90a1d0fefa8cc563` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151949-160129 |
| `cand-e43818f442f99457` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-15T19:50:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | SIGNATURE: 26/05/15 19:50 |
| `cand-e9190156a34fda2f` | `S1_llm_only` | `identifies_control_element` | BNA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA |
| `cand-edf499f7e3815731` | `S1_llm_only` | `states_estimated_coverage_window` | 15/2200Z - 16/0029Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 15/2200Z - 16/0029Z |
| `cand-f2c85dd82de94fb8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-2b647e8300e6828e` | `fact-2b647e8300e6828e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-fb027d5e1d95030d` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-15T22:00:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | ESTIMATED FOR: 15/2200Z - 16/0029Z |

## ATCSCC-GOLD-030 / 2026-05-16:027

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=81, est=24 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 39
- Cross-system clusters: 38
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05162026&advn=27

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: WORKING ON ROUTES EFFECTIVE TIME: 161146-161330 SIGNATURE: 26/05/16 11:46 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-0720e747af70b5ac` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00869a95ce5ad67b` | `S1_llm_only` | `reports_previous_maximum_delay` | 38 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-0d4d2c8dd1eb27a9` | `S1_llm_only` | `has_ground_stop_period` | 16/1045Z - 16/1230Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-1be7da6faa59aff6` | `S1_llm_only` | `has_control_element` | ORD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD |
| `cand-23414b3e121bb4a3` | `S1_llm_only` | `states_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-366446e577d2c2b5` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-16T11:42:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-05-88c2a21cb662` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z |
| `cand-3786918c3f513e75` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-0720e747af70b5ac` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-4528dd0261edf2c7` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-16T11:46:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/16 11:46 |
| `cand-4979f9719a1a948a` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-16T13:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-49850cb65e7a7118` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | ORD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-01-a59f9925619b` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-499503d62cf594dc` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ORD | `fact-72fb9c88fa0f2713` | `S1b_llm_canonicalized:2026-05-16:027:fact-0dcb6634d311, fact-72fb9c88fa0f2713` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: ORD |
| `cand-5545df3f73c9ae84` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-67a881b7ce8e3cf0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-16T11:46:00Z | `fact-84012af840cb805a` | `fact-84012af840cb805a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/16 11:46 |
| `cand-68478c5c9e6586e6` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-9d1cdac2c8a56d2e` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-03-a0c6de213ae5, fact-9d1cdac2c8a56d2e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6a70de4757e638b2` | `S2_llm_schema_slice` | `controlledNASelement` | ORD ELEMENT TYPE: APT | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: ORD ELEMENT TYPE: APT ADL TIME: 1142Z GROUND STOP PERIOD: 16/1045Z - 16/1230Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 3... |
| `cand-6db911b968c1e246` | `S1_llm_only` | `reports_previous_average_delay` | 26 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-700f4fec55598084` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-16T11:46:00Z | `fact-a85e3c467ce509d0` | `fact-a85e3c467ce509d0` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161146-161330 |
| `cand-79e95d4eef2301a9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 27 | `fact-030b0df5e739ff89` | `fact-030b0df5e739ff89` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP |
| `cand-7db1cf02fc0d89e3` | `S1_llm_only` | `has_effective_time` | 161146-161330 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-8381c764151965be` | `S1_llm_only` | `reports_previous_total_delays` | 156 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 156 / 38 / 26 |
| `cand-8468519072327e66` | `S1_llm_only` | `includes_departure_facility` | ZOB | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-893b4c852157e3ca` | `S1_llm_only` | `announces_ground_stop` | True | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CDM GROUND STOP |
| `cand-896eb124e418c6ab` | `S1_llm_only` | `reports_new_maximum_delay` | 78 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-8aa13fe14bbaeea4` | `S1_llm_only` | `reports_new_total_delays` | 403 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-93f87611c5f9e221` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-16T11:46:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 161146-161330 |
| `cand-94850e405ffe9619` | `S1_llm_only` | `identifies_impacting_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-9804b4d8db6a2f7d` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | WORKING ON ROUTES | `fact-bc27fdad22fa8f6e` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-04-f962c42f4f04, fact-bc27fdad22fa8f6e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | COMMENTS: WORKING ON ROUTES |
| `cand-9d42fa645984f761` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-9f4b484b36df2147` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-16T12:30:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-07-40a78f287b1d` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-aea0686f54cc3c1b` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-16T11:45:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-06-88fb4b927e95` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 16/1045Z - 16/1230Z |
| `cand-b216b2e3879a62ba` | `S2_llm_schema_slice` | `initiativeComments` | WORKING ON ROUTES | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: WORKING ON ROUTES |
| `cand-bd95bf6308d35814` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-cd4b3da7bf261930` | `S1b_llm_canonicalized:2026-05-16:027:fact-bcfe1e4b7526, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-02-33e2c997c6f1, fact-cd4b3da7bf261930` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-bed0902b85c44069` | `S1_llm_only` | `comments_on_route_work` | WORKING ON ROUTES | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: WORKING ON ROUTES |
| `cand-bf82b42e4351c3b2` | `S1_llm_only` | `reports_new_average_delay` | 67 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 403 / 78 / 67 |
| `cand-cc2359da4d2794d5` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d0095831a85453f1` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-16T13:30:00Z | `fact-7c7875b8835cf960` | `fact-7c7875b8835cf960` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 161146-161330 |
| `cand-dfa911f4880e0776` | `S1_llm_only` | `has_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-e0041a54a76982e0` | `S2_llm_schema_slice` | `type` | atm:GroundStopTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP |
| `cand-e0453736938ef38a` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-f3742cb71e05b537` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `departureScope` | {"properties": {"atm:includesAirport": [{"evidence_text": "DEP FACILITIES INCLUDED: (Manual) ZOB", "value": "ZOB"}]}, "type": "atm:Airpor... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-030:fact-08-54a05eb40cc0` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | DEP FACILITIES INCLUDED: (Manual) ZOB |

## ATCSCC-GOLD-009 / 2026-05-20:040

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=80, est=24 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 38
- Cross-system clusters: 38
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=40

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 040 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201000 TO 201400 PROBABILITY OF EXTENSION: MODERATE REMARKS: ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS < REDDN4 KMCO KORL KSFB ZMA KDFW >JAWJA MGMRY SARKK YUYUN < BEREE3 KMCO KORL KSFB ZMA KDAL >JAWJA MGMRY SARKK PUDJE < REDDN4 TMI ID: RRDCC504 EFFECTIVE TIME: 201000-201400 SIGNAT...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-0cb0d4d944029f9c` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-10a79bfcc41f76cc` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZFW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-19e5112d9c18f569` | `S1_llm_only` | `contains_route` | {'destination': 'KDAL', 'origin': 'KMCO', 'route': '>JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDAL >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS |
| `cand-1e55c9d11fad4b64` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 40 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-01-dd04e91948fb` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-1e6a57dc4419d7ea` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-05-1e0ef7ed7eb8` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-1f1bfc56f641d24a` | `S1_llm_only` | `contains_route` | {'destination': 'KDFW', 'origin': 'KMCO', 'route': '>JAWJA MGMRY SARKK YUYUN'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDFW >JAWJA MGMRY SARKK YUYUN |
| `cand-2b343e95dbbd5278` | `S1_llm_only` | `contains_route` | {'destination': 'KDFW', 'origin': 'KMCO', 'route': '>JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDFW >JAWJA CABLO DEFUN J2 CEW J50 AEX PNUTS |
| `cand-2e0f46a084b773fe` | `S1_llm_only` | `flight_status` | ALL_FLIGHTS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-4e8ef2e6e542643a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T10:00:00Z | `fact-c88128d827571110` | `fact-c88128d827571110` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201400 |
| `cand-583fe080fae3458a` | `S0_rule_only, S1b_llm_canonicalized` | `extensionProbability` | MODERATE | `fact-0cb0d4d944029f9c` | `` | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-58e1622086806d8c` | `S3_llm_schema_slice_validator_repair` | `reRouteType` | ROUTE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-03-b3579af42daa` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-5e15e959873d8035` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILIT... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-09-53dd165b5178` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-5f5aea3d0091bcda` | `S1_llm_only` | `has_name` | FLORIDA_TO_TEXAS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: FLORIDA_TO_TEXAS |
| `cand-68c31f8d5b6bbd72` | `S1_llm_only` | `probability_of_extension` | MODERATE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-714490a80e967b05` | `S1_llm_only` | `facilities_included` | ['ZFW', 'ZHU', 'ZJX', 'ZMA', 'ZME', 'ZTL'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-778af5a10a3efb1f` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-20T21:40:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-08-6c1e12da0825` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-7dd1801f6933f4a8` | `S1_llm_only` | `contains_route` | {'destination': 'KDAL', 'origin': 'KMCO', 'route': '>JAWJA MGMRY SARKK PUDJE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KMCO KORL KSFB ZMA KDAL >JAWJA MGMRY SARKK PUDJE |
| `cand-7fe14b7bcb284c7a` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-20T09:42:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-06-25a4aaa02fe0` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-8961e6f5af8f998e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZHU | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-89b2e71645d03738` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZME | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-8f0352d8836ca88f` | `S1_llm_only` | `has_constrained_area` | ZHU | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED AREA: ZHU |
| `cand-9372ccfe8e0cf13f` | `S1_llm_only` | `has_tmi_id` | RRDCC504 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC504 |
| `cand-9b741ec78d3ba0a5` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:KDAL | `` | `S1b_llm_canonicalized:2026-05-20:040:fact-d674928b42b0` | `{"repaired_accepted": 1}` | `{}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-9f28201aa744eb56` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-a3ab399d14ba65b6` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-b27d538207b95c0c` | `S3_llm_schema_slice_validator_repair` | `reRouteReason` | WEATHER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-04-14546e8d19a3` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-c26ad4906394c509` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:KDFW | `` | `S1b_llm_canonicalized:2026-05-20:040:fact-a3ba404ebfdd` | `{"repaired_accepted": 1}` | `{}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-c6dbeee9c81e7dd6` | `S1_llm_only` | `traffic_departures_to` | ['KDAL', 'KDFW'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-d055d0fd5785866d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T09:42:00Z | `fact-f4b9b8b7aaea8d13` | `fact-f4b9b8b7aaea8d13` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 09:42 |
| `cand-d23f81e142e0cf1e` | `S1_llm_only` | `valid_time_window` | ETD 201000 TO 201400 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201000 TO 201400 |
| `cand-d70b2b9465df72db` | `S1_llm_only` | `includes_traffic` | ['KMCO', 'KORL', 'KSFB', 'ZMA'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW |
| `cand-da648db2a59231f9` | `S1_llm_only` | `effective_time_window` | 201000-201400 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201000-201400 |
| `cand-dae2c1f9cec589a5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T14:00:00Z | `fact-1a73e6e6b5050c51` | `fact-1a73e6e6b5050c51` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201000-201400 |
| `cand-db974e25d7f0c051` | `S1_llm_only` | `has_reason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-dec998ca4d2499fa` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 40 | `fact-1a33ab7acb1f5b25` | `fact-1a33ab7acb1f5b25` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 040 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-ea11f1a110777bb8` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-f47eb5038aeb111d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL |
| `cand-f9abdecb067cb7c3` | `S3_llm_schema_slice_validator_repair` | `implementationStatus` | RQD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-02-273f953fa2a5` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |
| `cand-fdd4c0108d8964a9` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-20T20:10:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-009:fact-07-1487ec251603` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: NAME: FLORIDA_TO_TEXAS CONSTRAINED AREA: ZHU REASON: WEATHER INCLUDE TRAFFIC: KMCO/KORL/KSFB/ZMA DEPARTURES TO KDAL/KDFW FACILITIES INCLUDED: ZFW/ZHU/ZJX/ZMA/ZME/ZTL FL... |

## ATCSCC-GOLD-016 / 2026-05-20:078

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=79, est=24 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 38
- Cross-system clusters: 37
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=78

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCLUDED: ZBW/ZDC/ZOB FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 201315 TO 201830 PROBABILITY OF EXTENSION: MODERATE REMARKS: REPLACES ADVZY 056. FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE FLIGHT. IMPLEMENTED DUE TO SPECIAL OPERATIONS ASSOCIATED RESTRICTIONS: MODIFICATIONS: END TIME EXTENDED. ROUTES: ORIG DEST ROUTE ---- ---- ----- KBWI KDCA KIAD KBOS >JERES J211 LEONI WEVEL ELZ VIEEW ITH PONCT < JFUND2 TMI ID: RRDCC508 EFFECTIVE TIME: 201315-201830 SIGNATURE: 26/05/20...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-25fe34b8b2db4bf7` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-000953b235d1a9d8` | `S1_llm_only` | `'must_not_request_above'}` | {'label': 'FL220', 'type': 'altitude_limit'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE FLIGHT. |
| `cand-0f29fd5c2dffb2db` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteReason` | OTHER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-016:fact-03-9ebeb531cc00` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCL... |
| `cand-2267999d52c0d9a1` | `S1_llm_only` | `'replaces_advisory'}` | {'label': 'ADVZY 056', 'type': 'prior_advisory'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REPLACES ADVZY 056. |
| `cand-2727451e105a4ff7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteType` | ROUTE | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-016:fact-02-6164e5d072ac` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCL... |
| `cand-2bce43f56f5f46b2` | `S2_llm_schema_slice` | `implementationStatus` | RQD | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-2bf45f9d2b707d2a` | `S1_llm_only` | `'has_area'}` | {'label': 'ZBW', 'type': 'air_traffic_area'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW |
| `cand-2dd1617cc2a77706` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZBW/ZDC/ZOB |
| `cand-3dd8b45f2cadb13d` | `S1_llm_only` | `'applies_to_flight_status'}` | {'label': 'ALL_FLIGHTS', 'type': 'flight_status'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-51009f836a81f1d6` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-016:fact-04-c4870689d4b3` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCL... |
| `cand-637d12d40772d38f` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | REPLACES ADVZY 056. FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE F... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-016:fact-05-75d1dadfc3fe` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCL... |
| `cand-6c0ab336f2a21de9` | `S2_llm_schema_slice` | `reRouteType` | ROUTE | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-70bb5fe0fbf1da0a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T13:15:00Z | `fact-44a53a3b77c1b1e0` | `fact-44a53a3b77c1b1e0` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201315-201830 |
| `cand-7eb98dc929ae878f` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T20:13:15Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | VALID: ETD 201315 TO 201830 |
| `cand-8a25383ed7bdd975` | `S1b_llm_canonicalized` | `advisoryNumber` | 78 | `` | `S1b_llm_canonicalized:2026-05-20:078:fact-05eccda623a9` | `{"repaired_accepted": 1}` | `{}` | REPLACES ADVZY 056. |
| `cand-a155d7623ded46de` | `S2_llm_schema_slice` | `initiativeComments` | REPLACES ADVZY 056. FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE F... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | REMARKS: REPLACES ADVZY 056. FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. DO NOT REQUEST AN ALTITUDE HIGHER THAN FL220 DURING THE ENTIRE FLIGHT. IMPLEMENTED DUE TO SPECI... |
| `cand-b05e0fcf3db38857` | `S1_llm_only` | `'has_route'}` | {'label': 'KBWI KDCA KIAD KBOS >JERES J211 LEONI WEVEL ELZ VIEEW ITH PONCT', 'type': 'route_sequence'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ROUTES: ORIG DEST ROUTE ---- ---- ----- KBWI KDCA KIAD KBOS >JERES J211 LEONI WEVEL ELZ VIEEW ITH PONCT |
| `cand-b1bb2beb2cfcec65` | `S1b_llm_canonicalized` | `impactingCondition` | other reason_category | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: OTHER |
| `cand-b43f3af4a01c371d` | `S1_llm_only` | `'valid_during'}` | {'label': '201315 TO 201830', 'type': 'time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 201315 TO 201830 |
| `cand-b71df8bd1906acfd` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T15:56:00Z | `fact-dc5ad899186e4242` | `fact-dc5ad899186e4242` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 15:56 |
| `cand-b72fc3268b306e2b` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T20:18:30Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | VALID: ETD 201315 TO 201830 |
| `cand-ba3c6095023a5a9c` | `S1_llm_only` | `'must_comply_with'}` | {'label': 'ALTITUDE_RESTRICTIONS', 'type': 'operational_restriction'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT CREWS MUST COMPLY WITH ALTITUDE RESTRICTIONS. |
| `cand-bc4c89fb7adedc7e` | `S1_llm_only` | `'implemented_due_to'}` | {'label': 'SPECIAL OPERATIONS ASSOCIATED RESTRICTIONS', 'type': 'implementation_cause'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPLEMENTED DUE TO SPECIAL OPERATIONS ASSOCIATED RESTRICTIONS: |
| `cand-bf7ebd6b88aa3d52` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 78 | `fact-7b32848cfd156a29` | `fact-7b32848cfd156a29` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-c2f968d64c2100c0` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-016:fact-01-7b4d3d893f50` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS FACILITIES INCL... |
| `cand-c365bed46c8883b6` | `S1_llm_only` | `'has_facilities_included'}` | {'label': 'ZBW/ZDC/ZOB', 'type': 'facility_group'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: ZBW/ZDC/ZOB |
| `cand-c640120243b2451d` | `S0_rule_only` | `extensionProbability` | MODERATE | `fact-25fe34b8b2db4bf7` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-c9931676aca2f027` | `S1_llm_only` | `'has_probability_of_extension'}` | {'label': 'MODERATE', 'type': 'extension_probability'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-cd493132fe30ae38` | `S1_llm_only` | `'includes_traffic'}` | {'label': 'KBWI/KDCA/KIAD DEPARTURES TO KBOS', 'type': 'traffic_group'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS |
| `cand-d4bff2bc96d35231` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-e0105fe74fb97f12` | `S1_llm_only` | `'has_tmi_id'}` | {'label': 'RRDCC508', 'type': 'tmi_identifier'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | JFUND2 TMI ID: RRDCC508 |
| `cand-e22c4e30b65b1c1c` | `S1_llm_only` | `'effective_time'}` | {'label': '201315-201830', 'type': 'effective_time_window'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 201315-201830 |
| `cand-e38d716c5dcbb0f5` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T18:30:00Z | `fact-45d709cf29039e0d` | `fact-45d709cf29039e0d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 201315-201830 |
| `cand-e3a3296956cc3b6a` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZBW/ZDC/ZOB |
| `cand-e9e9cd052a76700f` | `S2_llm_schema_slice` | `controlledNASelement` | nas:ARTCC/ZBW | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS |
| `cand-eed535e06f4b9010` | `S1_llm_only` | `'has_reason'}` | {'label': 'OTHER', 'type': 'reason_category'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: OTHER |
| `cand-f15e97454a437f6f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: ZBW/ZDC/ZOB |
| `cand-f52486944b51a6bc` | `S2_llm_schema_slice` | `reRouteReason` | OTHER | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | NAME: WEVEL_PARTIAL CONSTRAINED AREA: ZBW REASON: OTHER INCLUDE TRAFFIC: KBWI/KDCA/KIAD DEPARTURES TO KBOS |
| `cand-fbd7bd7cf1c43d5a` | `S1_llm_only` | `'has_modification'}` | {'label': 'END TIME EXTENDED', 'type': 'modification'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MODIFICATIONS: END TIME EXTENDED. |

## ATCSCC-GOLD-032 / 2026-05-20:131

- Batch: `batch_04`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_04.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=79, est=24 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 38
- Cross-system clusters: 37
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=131

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1957Z GROUND STOP PERIOD: 20/1947Z - 20/2130Z DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1387 / 68 / 30 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 4276 / 171 / 93 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: GROUND STOP EXTENSION. EFFECTIVE TIME: 202001-202230 SIGNATURE: 26/05/20 20:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-89a2b2dbb8dc0f28` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-01cba1d2d80202de` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T20:02:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/20 20:02 |
| `cand-048fee988a78248c` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-09a2e65fccc4356a` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-0cecac67571972d3` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-89a2b2dbb8dc0f28` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-0f52982a0bb296cf` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZJX | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-0f76f643acccc6a2` | `S2_llm_schema_slice` | `advisoryNumber` | 131 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-1518fddef0e615c6` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:IAD | `fact-ae19577e34f32582` | `S1b_llm_canonicalized:2026-05-20:131:fact-1b67c9eac8e0, fact-ae19577e34f32582` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: IAD |
| `cand-15e8170ed2ec2143` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T22:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-285cf9794786b0e9` | `S1_llm_only` | `has_effective_time` | 202001-202230 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-34276ef6718793bd` | `S1_llm_only` | `has_control_element` | IAD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD |
| `cand-369e08f75f61c1d6` | `S1_llm_only` | `has_previous_delays` | 1387 / 68 / 30 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 1387 / 68 / 30 |
| `cand-39a1abda6cd9af66` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T22:30:00Z | `fact-461a169542bd65d6` | `fact-461a169542bd65d6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202001-202230 |
| `cand-3bc01047634f840d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-559051b34033e226` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 131 | `fact-af23796e09fff2b5` | `fact-af23796e09fff2b5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-574fc65e2a607b02` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | IAD | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-032:fact-01-1b5dea757ce6` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1957Z GROUND STOP PERIOD: 20/1947Z - 20/2130Z |
| `cand-582b30d1bba81ca1` | `S2_llm_schema_slice` | `type` | atm:GroundStopTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `cand-5853ec918889485b` | `S2_llm_schema_slice` | `initiativeComments` | GROUND STOP EXTENSION. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: GROUND STOP EXTENSION. |
| `cand-63e8c9f983ba75e6` | `S2_llm_schema_slice` | `controlledNASelement` | IAD | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: IAD |
| `cand-653c7ec30a58c5ea` | `S1_llm_only` | `describes_ground_stop_period` | 20/1947Z - 20/2130Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/1947Z - 20/2130Z |
| `cand-71d614307d685413` | `S1_llm_only` | `includes_departure_facilities` | ZTL ZDC ZNY ZJX ZOB ZBW ZID | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-799724068c0f8b08` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-7d4e7c1653d439f6` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZTL | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-87a5344e48c1e019` | `S1_llm_only` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-89574b09b53466fc` | `S1_llm_only` | `has_new_delays` | 4276 / 171 / 93 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 4276 / 171 / 93 |
| `cand-9ae972c0cb147f8a` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | GROUND STOP EXTENSION. | `fact-26139314fea56c23` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-032:fact-04-03bdbcdf70b6, fact-26139314fea56c23` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | COMMENTS: GROUND STOP EXTENSION. |
| `cand-9cd88ea728114406` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-8f5a61cbad2356cd` | `S1b_llm_canonicalized:2026-05-20:131:fact-bcfe1e4b7526, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-032:fact-02-8364288cb312, fact-8f5a61cbad2356cd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a363f3f25ccd48ab` | `S1_llm_only` | `has_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-ac02906fd37ffdf1` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-aefa9ea47d53bcda` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T20:01:00Z | `fact-490bc4932ffee2db` | `fact-490bc4932ffee2db` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202001-202230 |
| `cand-b5ebc6374cde5b96` | `S1_llm_only` | `has_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-cfefdaf9d2e28bc5` | `S1_llm_only` | `has_adl_time` | 1957Z | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_object_class": 1, "unknown_predicate": 1, "unknown_s...` | ADT TIME: 1957Z |
| `cand-db075fab5859e21d` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-dcde26be1a0b3848` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-ded5bbdc4293fe5b` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T20:02:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202001-202230 |
| `cand-e79119e757730bcf` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-a532f9e62375f64c` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-032:fact-03-403127857ab1, fact-a532f9e62375f64c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e9a9d34342e3c8e0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T20:02:00Z | `fact-ebdfb593a42634f7` | `fact-ebdfb593a42634f7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 20:02 |
| `cand-f6afff5b16c335ca` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZTL ZDC ZNY ZJX ZOB ZBW ZID |
| `cand-fcc83705f4d342d9` | `S1_llm_only` | `has_comment` | GROUND STOP EXTENSION. | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: GROUND STOP EXTENSION. |

## ATCSCC-GOLD-059 / 2026-05-14:086

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=79, est=23 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 38
- Cross-system clusters: 37
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=86

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 142157-150230 SIGNATURE: 26/05/14 21:57 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-a1fe57a7c1e7da35` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-011c8a168d17f0a6` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 86 | `fact-12ccb88b34496453` | `S1b_llm_canonicalized:2026-05-14:086:fact-cb7a7a2dd511, S2_llm_schema_slice:ATCSCC-GOLD-059:fact-01-e66c3c365587, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-059:fact-01-e66c3c365587, fact-12ccb88b34496453` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 4}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-044ec392d6c4e4a3` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-15T02:30:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-04-666e85a7cb4f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-068d97afee5ef5a9` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FO... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-059:fact-05-85108030a561` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-0d7053deeec50e64` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-06-6df0a2db5aa9` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-1102bd9b1fd2dea5` | `S1_llm_only` | `identifies_constrained_facility` | ZMP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZMP |
| `cand-16810545d5bd5746` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-11-9bb627e0d82a` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORM... |
| `cand-17196c2fba410527` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-17f704b0aa1cdbda` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THE | `fact-53acb2f3f6785536` | `fact-53acb2f3f6785536` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-19c576a61f2066c5` | `S1_llm_only` | `has_advisory_title` | MSP AIRPORT ARRIVAL DELAYS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-42b3b6f82a405cdd` | `S2_llm_schema_slice` | `initiativeComments` | MSP AIRPORT ARRIVAL DELAYS | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-05-d3ce5d153349` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-4618c852fcf78b7f` | `S1_llm_only` | `states_event_time_window` | 14/2200 - 15/0200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/2200 - 15/0200 |
| `cand-5b02bc7158ad4af0` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-14T21:57:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-059:fact-02-a73f4dbca0c9` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 21:57 |
| `cand-65b8b507ef633b2c` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-14T21:57:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-03-15950f84b453` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-660e4d7494b665a4` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-15T02:30:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-10-a9441834ac2c` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORM... |
| `cand-6f894e047871ea17` | `S1_llm_only` | `concerns_facility_group` | MSP/ZMP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-76a209f892c9e52d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `fact-9dbf14cd723164ec` | `fact-9dbf14cd723164ec` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-82c657b167983f84` | `S1_llm_only` | `says_users_can_expect` | arrival delays | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-891c6111be54ac7b` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `fact-a1fe57a7c1e7da35` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-8daf6f6ccbccede4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `fact-cd1c5562c68927e3` | `fact-cd1c5562c68927e3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-9ebf908fd6516b39` | `S1_llm_only` | `gives_delay_cause` | thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-a215b06645b62fce` | `S1_llm_only` | `says_users_can_expect` | airborne holding into the Minneapolis airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-b115dfe6df279bb0` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMP |
| `cand-b38bfb7831639137` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T21:57:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-08-ec57e6bfed92` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORM... |
| `cand-b538f124c8ca3a9a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T02:30:00Z | `fact-5919b62aa1e99898` | `fact-5919b62aa1e99898` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142157-150230 |
| `cand-b64e386fa83817f7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T21:57:00Z | `fact-e5c75c78e521e008` | `fact-e5c75c78e521e008` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 21:57 |
| `cand-ba36a24473c0a65b` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T21:57:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-02-1245baa1b4cc` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-bbb6ccd1012a5bcc` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-14T22:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-059:fact-03-17ef7dc4eb77` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 |
| `cand-bc80e0c4447959d8` | `S1_llm_only` | `promises_follow_up_updates` | if necessary | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-bcd80a5d897c39b3` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-14T21:57:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-09-7cd8028b949e` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORM... |
| `cand-beb0fb2aa07ca50f` | `S1_llm_only` | `gives_delay_duration` | up to 30 minutes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-c1528aa6b326016e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MSP | `` | `S1b_llm_canonicalized:2026-05-14:086:fact-812ae2b06a65` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `cand-c2091a2db9b95b78` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `fact-89533045d4fa2a20` | `fact-89533045d4fa2a20` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES |
| `cand-c352f1ea8b5585e9` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-15T02:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-059:fact-04-c4e8dec9d5f0` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 |
| `cand-d96b06b77ee8cc61` | `S2_llm_schema_slice` | `advisoryNumber` | 86 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-07-f95968cfcbcc` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORM... |
| `cand-e125c3d602fab938` | `S1_llm_only` | `states_effective_time` | 142157-150230 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 142157-150230 |
| `cand-e53580f163a7233c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T21:57:00Z | `fact-d45ec3167c141f9b` | `fact-d45ec3167c141f9b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 142157-150230 |
| `cand-edb85d0347e07219` | `S1b_llm_canonicalized` | `impactingCondition` | thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. |
| `cand-fba80025a85444d8` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-059:fact-12-c752d51798df` | `{"repaired_accepted": 1}` | `{}` | EVENT TIME: 14/2200 - 15/0200 CONSTRAINED FACILITIES: ZMP USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE MINNEAPOLIS AIRPORT OF UP TO 30 MINUTES DUE TO THUNDERSTORM... |

## ATCSCC-GOLD-015 / 2026-05-20:137

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=78, est=24 min)
- Candidate class: `ReRouteTMI`
- Candidate clusters: 37
- Cross-system clusters: 37
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=137

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL MESSAGE: NAME: GREKI_1 CONSTRAINED AREA: ZNY REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES TO CYYZ/KBUF/KROC/KSYR FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB FLIGHT STATUS: ALL_FLIGHTS VALID: ETD 202030 TO 210200 PROBABILITY OF EXTENSION: MODERATE REMARKS: FOR JETS ONLY AOB FL220 ASSOCIATED RESTRICTIONS: MODIFICATIONS: ROUTES: ORIG DEST ROUTE ---- ---- ----- KEWR KJFK KLGA KBUF >GREKI JUDDS CAM SYR ROC KHPN KTEB EHMAN < KEWR KJFK KLGA CYYZ >GREKI JUDDS CAM Q822 GONZZ KHPN KTEB WOZEE < LINNG3 KEWR KJFK KLGA KSYR >GREKI JUDDS CAM < KHPN KTEB KEWR KJFK KLGA KROC >GREKI JUDDS CAM Q822 KHPN KTEB GONZZ < TMI ID: RRDCC137 EFFECTIVE TIME: 202030-210200...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-83bba681dfc4a57d` | `extensionProbability` | `allowed_value_violation` | `extractor_normalization_bug_candidate` | PROBABILITY OF EXTENSION: MODERATE |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0acd71cfcb3f5c82` | `S1_llm_only` | `has route modification` | {'destination': 'KSYR', 'origin': ['KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | LINNG3 KEWR KJFK KLGA KSYR >GREKI JUDDS CAM |
| `cand-0d1b05af1e528f1f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CZY | `` | `S1b_llm_canonicalized:2026-05-20:137:fact-a11d4470397a` | `{"repaired_accepted": 1}` | `{}` | FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB |
| `cand-1076ee6e3a7167f3` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED AREA: ZNY |
| `cand-11f91e0739c64db5` | `S2_llm_schema_slice` | `initiativeComments` | FOR JETS ONLY AOB FL220 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-10-5d655a1d9a14` | `{"repaired_accepted": 1}` | `{}` | REMARKS: FOR JETS ONLY AOB FL220 |
| `cand-17099df4617b05da` | `S1_llm_only` | `has route modification` | {'destination': 'KBUF', 'origin': ['KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM SYR ROC KHPN KTEB EHMAN'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KEWR KJFK KLGA KBUF >GREKI JUDDS CAM SYR ROC KHPN KTEB EHMAN |
| `cand-1cb1a6184dde4061` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-21T02:00:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-09-2af229b2e9e1` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202030-210200 |
| `cand-1f32e2d760453b3a` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T20:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-08-e8c81a1494d6` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202030-210200 |
| `cand-2ad97d94fded7d85` | `S1_llm_only` | `flight status` | ALL_FLIGHTS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLIGHT STATUS: ALL_FLIGHTS |
| `cand-2fa074849ad0bbfa` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 137 | `fact-905911c2d749657b` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-01-419686ab9542, fact-905911c2d749657b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-2fdaaa55eeb81e92` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZBW | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB |
| `cand-34a0d95aff5cb7b2` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `implementationStatus` | RQD | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-03-259491e9c5f2, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-015:fact-02-259491e9c5f2` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL |
| `cand-34b59dbe8370fa02` | `S2_llm_schema_slice` | `reRouteReason` | WEATHER | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-04-7b22ccc2b456` | `{"repaired_accepted": 1}` | `{}` | NAME: GREKI_1 CONSTRAINED AREA: ZNY REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES TO CYYZ/KBUF/KROC/KSYR FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB FLIGHT STATU... |
| `cand-35a7fcc947ebba90` | `S1_llm_only` | `has route modification` | {'destination': 'CYYZ', 'origin': ['KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM Q822 GONZZ KHPN KTEB WOZEE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KEWR KJFK KLGA CYYZ >GREKI JUDDS CAM Q822 GONZZ KHPN KTEB WOZEE |
| `cand-42036b369bdfc5e9` | `S1_llm_only` | `probability of extension` | MODERATE | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-482652dc34980d0d` | `S1_llm_only` | `facilities included` | ['CZY', 'ZBW', 'ZNY', 'ZOB'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB |
| `cand-4f99d15f196f1afa` | `S1_llm_only` | `remark` | FOR JETS ONLY AOB FL220 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REMARKS: FOR JETS ONLY AOB FL220 |
| `cand-67b390a025f30e05` | `S1_llm_only` | `valid time window` | 202030 to 210200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | VALID: ETD 202030 TO 210200 |
| `cand-78a543790a5bface` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB |
| `cand-7cc99458be815aff` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-21T02:00:00Z | `fact-264fb2d28e296708` | `fact-264fb2d28e296708` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202030-210200 |
| `cand-80a38c3b5419b82f` | `S1b_llm_canonicalized` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | REASON: WEATHER |
| `cand-88f62e056de7f267` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T20:30:00Z | `fact-265d359a0a146689` | `fact-265d359a0a146689` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202030-210200 |
| `cand-8c159fae1eb4b1d5` | `S1_llm_only` | `has route modification` | {'destination': 'KROC', 'origin': ['KHPN', 'KTEB', 'KEWR', 'KJFK', 'KLGA'], 'route': 'GREKI JUDDS CAM Q822 KHPN KTEB GONZZ'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | KHPN KTEB KEWR KJFK KLGA KROC >GREKI JUDDS CAM Q822 KHPN KTEB GONZZ |
| `cand-941293638a9be22c` | `S0_rule_only, S1b_llm_canonicalized` | `extensionProbability` | MODERATE | `fact-83bba681dfc4a57d` | `` | `{"rejected_schema": 2}` | `{"allowed_value_violation": 2}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-9f17faf10042c10e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T20:38:00Z | `fact-2c9164d30ab866f4` | `fact-2c9164d30ab866f4` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 20:38 |
| `cand-a7c66c0adba2fb22` | `S2_llm_schema_slice` | `controlledNASelement` | ZNY | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-02-9966495a730c` | `{"repaired_accepted": 1}` | `{}` | NAME: GREKI_1 CONSTRAINED AREA: ZNY REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES TO CYYZ/KBUF/KROC/KSYR FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB FLIGHT STATU... |
| `cand-ba7f25c1380487da` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB |
| `cand-bf0d6b3ac009cb8a` | `S1_llm_only` | `tmi identifier` | RRDCC137 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TMI ID: RRDCC137 |
| `cand-c522df176e47fef0` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-06-c3b1a3d336a9` | `{"repaired_accepted": 1}` | `{}` | NAME: GREKI_1 CONSTRAINED AREA: ZNY REASON: WEATHER INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES TO CYYZ/KBUF/KROC/KSYR FACILITIES INCLUDED: CZY/ZBW/ZNY/ZOB FLIGHT STATU... |
| `cand-d28c57371c92539e` | `S1_llm_only` | `includes traffic` | ['KEWR departures', 'KHPN departures', 'KJFK departures', 'KLGA departures', 'KTEB departures'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES |
| `cand-d3a58e36a3b95f91` | `S1_llm_only` | `effective time` | 202030-210200 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202030-210200 |
| `cand-d76129a10c51f4c7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteReason` | WEATHER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-015:fact-03-66dcc9eb0c57` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | REASON: WEATHER |
| `cand-dcfa8169f94f18ba` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-20T20:38:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-07-41ed928fd47e` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/20 20:38 |
| `cand-ea84d54da54408e1` | `S1_llm_only` | `is constrained area in` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NAME: GREKI_1 CONSTRAINED AREA: ZNY |
| `cand-f07e9985cd6f4c81` | `S1_llm_only` | `has reason` | WEATHER | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | REASON: WEATHER |
| `cand-f1f57fabe68fb12b` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-015:fact-01-ed7520296181` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | PROBABILITY OF EXTENSION: MODERATE |
| `cand-f3608b190f790a8b` | `S1_llm_only` | `applies to destinations` | ['CYYZ', 'KBUF', 'KROC', 'KSYR'] | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | INCLUDE TRAFFIC: KEWR/KHPN/KJFK/KLGA/KTEB DEPARTURES TO CYYZ/KBUF/KROC/KSYR |
| `cand-f36b9d1bf7b116bc` | `S2_llm_schema_slice, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `reRouteType` | ROUTE | `` | `S2_llm_schema_slice:ATCSCC-GOLD-015:fact-05-cad6c477e010, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-015:fact-04-cad6c477e010` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL |

## ATCSCC-GOLD-004 / 2026-05-14:059

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=75, est=22 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 36
- Cross-system clusters: 35
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05142026&advn=59

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ EFFECTIVE TIME: 141554-150100 SIGNATURE: 26/05/14 15:54 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-4c3d4291069aa8d2` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-05dd9896c47dbe78` | `S1_llm_only` | `include_airports` | CDW | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-081409a19a4378e1` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LDJ | `` | `S1b_llm_canonicalized:2026-05-14:059:fact-99035fe3bd90` | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-0bbd1b59e59fe3b9` | `S1_llm_only` | `include_airports` | TEB | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-1e4fba32b4173686` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:AND | `fact-2e69c4b6702a9a13` | `fact-2e69c4b6702a9a13` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-33eaaeb689026678` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-14T17:00:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS... |
| `cand-38e5510e0e91a92a` | `S1_llm_only` | `identifies_event_time_window` | 14/1700 - 15/0100 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 14/1700 - 15/0100 |
| `cand-488f2a1cafbc0317` | `S2_llm_schema_slice` | `initiativeComments` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES DUE TO COMPACTED DEM... | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS... |
| `cand-4f39e89cea945d3e` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:TEB | `` | `S1b_llm_canonicalized:2026-05-14:059:fact-98ed1a2ff3f5` | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-5081f2e4fa6feb09` | `S2_llm_schema_slice` | `advisoryNumber` | 59 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS... |
| `cand-57a317dce08fb9ee` | `S1_llm_only` | `are_due_to` | compacted demand | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-57c974c97ed81aad` | `S1_llm_only` | `include_airports` | LDJ | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-57fedf1035dd8294` | `S1_llm_only` | `names_constrained_facility_area` | ZNY | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-5f0a41c1b63f8abb` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-14T15:54:00Z | `fact-6eab554ac0950983` | `fact-6eab554ac0950983` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/14 15:54 |
| `cand-6203c4af64f5d13a` | `S1_llm_only` | `promises_updates` | will follow if necessary | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-630c6bc8d4872b95` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 59 | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-632776e237be985f` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-14T15:54:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-663abc1431a9004e` | `S1_llm_only` | `states_event_title` | EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-688b63b83e7e709a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `fact-3ddbaf7e781caecb` | `fact-3ddbaf7e781caecb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-6f0b917db886a229` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CDW | `` | `S1b_llm_canonicalized:2026-05-14:059:fact-ea8d83748aa5` | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-74943c40174a0219` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-14T15:54:00Z | `fact-cec25cfae235830a` | `fact-cec25cfae235830a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141554-150100 |
| `cand-7ef12c8f255a55d3` | `S1_llm_only` | `can_expect_arrival_delays_and_airborne_holding_into` | Newark and Newark satellite airports | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS |
| `cand-862daff7ccf60ce2` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY |
| `cand-8be9337afe7b0d43` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-15T01:00:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS... |
| `cand-8cd2f614737f070c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-15T01:00:00Z | `fact-73c77c0341b48f84` | `fact-73c77c0341b48f84` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 141554-150100 |
| `cand-991ef3be833b58fb` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES DUE TO COMPACTED DEM... | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-9a29660c620c0051` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZNY | `fact-4c3d4291069aa8d2` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-a7429d149fe9768e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `fact-cd83678d6d329f52` | `fact-cd83678d6d329f52` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-b2e6dbd780a6b160` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-15T01:00:00Z | `` | `` | `{"rejected_evidence": 1}` | `{"missing_evidence": 1}` |  |
| `cand-da48274e4242a4bf` | `S1_llm_only` | `have_reported_maximum_duration` | up to 30 minutes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | OF UP TO 30 MINUTES |
| `cand-da96febd410296f6` | `S2_llm_schema_slice` | `extensionProbability` | LOW | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS... |
| `cand-dad475c94e2a63a1` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 59 | `fact-57e50517cac76939` | `S1b_llm_canonicalized:2026-05-14:059:fact-7892a46d9670, fact-57e50517cac76939` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-ea9f08b0c6952725` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MMU | `` | `S1b_llm_canonicalized:2026-05-14:059:fact-3cc506fceec8` | `{"repaired_accepted": 1}` | `{}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-ed0214bafea35c13` | `S1_llm_only` | `include_airports` | MMU | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EWR SATELLITE AIRPORTS INCLUDE BUT ARE NOT LIMITED TO PHL AREA C MUGZY SECTOR AIRPORTS SUCH AS TEB, MMU ,CDW, AND LDJ |
| `cand-eeaf7c3ed2af20f8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `fact-a884a5822005a954` | `fact-a884a5822005a954` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO NEWARK AND NEWARK SATELLITE AIRPORTS OF UP TO 30 MINUTES |
| `cand-f313f0473b7aa861` | `S2_llm_schema_slice` | `controlledNASelement` | {"@type": "nas:Airport", "evidence_text": "EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS"} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_subject_class": 1}` | EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `cand-fb9941fa47c94fc4` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-14T15:54:00 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 14/1700 - 15/0100 CONSTRAINED FACILITIES: ZNY USERS CAN EXPECT ARRIVAL DELAYS... |

## ATCSCC-GOLD-028 / 2026-05-18:123

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=75, est=22 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 36
- Cross-system clusters: 35
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=123

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: NO ROUTES EFFECTIVE TIME: 182022-182230 SIGNATURE: 26/05/18 20:25 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-bba6f91e8b7d3bf8` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-08d1954bd885399d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T20:25:00Z | `fact-db678b1297a5d1d5` | `fact-db678b1297a5d1d5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 20:25 |
| `cand-09e4c7e007198561` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T20:22:00Z | `fact-fc9505e8c3c5786e` | `fact-fc9505e8c3c5786e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182022-182230 |
| `cand-11a622cab58e1040` | `S1_llm_only` | `has_new_total_delay` | 39 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-223627f9f7adef81` | `S1_llm_only` | `has_previous_average_delay` | 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-2909877ace983808` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-3180705419906a34` | `S1_llm_only` | `includes_departure_facility` | ZOB | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-4125941f77efcb3d` | `S1_llm_only` | `announces_ground_stop_for` | MSP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `cand-490a0fe8225fac2c` | `S1_llm_only` | `became_effective_at` | 182022-182230 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-4d0ff8823bad4100` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T20:22:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-5e2f1cfff8539887` | `S1_llm_only` | `has_new_average_delay` | 39 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-5ffebbbf03aebf75` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport:MSP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: MSP ELEMENT TYPE: APT |
| `cand-66456ed62716af4c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MSP | `fact-d1647e1f6191131f` | `fact-d1647e1f6191131f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP |
| `cand-693735614a3e2887` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `fact-72c000e3f743d211` | `fact-72c000e3f743d211` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182022-182230 |
| `cand-733a50d70b8e6531` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182022-182230 |
| `cand-77ca277b4c5d3335` | `S1_llm_only` | `has_comment` | NO ROUTES | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: NO ROUTES |
| `cand-7b0b7ab29f3078cb` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | MSP | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-028:fact-01-230b9ca59dde` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 /... |
| `cand-7ecc4cb91bfc0471` | `S1_llm_only` | `is_controlled_by` | CTL ELEMENT MSP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z |
| `cand-826af240adb0a231` | `S1_llm_only` | `has_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-8ea4cb33d45cfb93` | `S2_llm_schema_slice` | `initiativeComments` | NO ROUTES | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | COMMENTS: NO ROUTES |
| `cand-90a62edcb56ffbd7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-028:fact-03-0bec7bf74fb6` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 /... |
| `cand-948713c9bdc22713` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T20:25:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |
| `cand-9ae9e8ac06fa4d18` | `S1_llm_only` | `has_ground_stop_period` | 18/2009Z - 18/2130Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2009Z - 18/2130Z |
| `cand-9bbbec8ae25034dc` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | NO ROUTES | `fact-b642bf5c196142c6` | `fact-b642bf5c196142c6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: NO ROUTES |
| `cand-a85b70ddae55179b` | `S1_llm_only` | `has_previous_total_delay` | 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-ae390ab31a84b437` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-bba6f91e8b7d3bf8` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-b14c415e3b61ecc1` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 123 | `fact-db2d48b470ffd320` | `S1b_llm_canonicalized:2026-05-18:123:fact-ee32dea2e367, fact-db2d48b470ffd320` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `cand-b19ec6a1c326993a` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-028:fact-02-1f7bae271c1c` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: MSP ELEMENT TYPE: APT ADL TIME: 2019Z GROUND STOP PERIOD: 18/2009Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZOB PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 /... |
| `cand-b56d2453f7034ff8` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZOB |
| `cand-ba8ff158e1a5028b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-dd3b7933661d1b0c` | `fact-dd3b7933661d1b0c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-cf42983557624190` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-db01fbb5859bf645` | `S1b_llm_canonicalized:2026-05-18:123:fact-bcfe1e4b7526, fact-db01fbb5859bf645` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d1d78f2760a13c55` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d52e05122fc668b1` | `S1_llm_only` | `was_signed_at` | 26/05/18 20:25 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:25 |
| `cand-e6ba863cd1d13331` | `S1_llm_only` | `has_previous_maximum_delay` | 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-f01e77005ea9fd6f` | `S1_llm_only` | `has_new_maximum_delay` | 39 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 39 / 39 / 39 |
| `cand-f256d1d94d4ef553` | `S1_llm_only` | `is_impacted_by_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-f90c0d71e551cd6f` | `S2_llm_schema_slice` | `type` | atm:GroundStopTMI | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |

## ATCSCC-GOLD-017 / 2026-05-19:079

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=73, est=22 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 35
- Cross-system clusters: 34
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=79

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0359Z CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0359Z PROGRAM RATE: 28/28/28/24/20/20/20/20 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: NONE DELAY ASSIGNMENT TABLE APPLIES TO: ZME MAXIMUM DELAY: 106 AVERAGE DELAY: 54 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. EFFECTIVE TIME: 191854-200459 SIGNATURE: 26/05/19 18:55 FAA.gov Home \| Privacy Policy \| Web Pol...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-55ba0ebe57eb90f0` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-045894776386df86` | `S1_llm_only` | `'has_maximum_delay_minutes'}` | {'label': '106'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 106 |
| `cand-06de3134b9a05d97` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-20T04:59:00Z | `fact-95336e133bba0e2e` | `fact-95336e133bba0e2e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191854-200459 |
| `cand-0980b0a0c641cc85` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:NONE | `` | `S1b_llm_canonicalized:2026-05-19:079:fact-f1cb32e0390a` | `{"repaired_accepted": 1}` | `{}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-1786046715839746` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | BNA | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-017:fact-01-2fcf8080e337` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM |
| `cand-17e325a715f90cb9` | `S1_llm_only` | `'has_delay_assignment_mode'}` | {'label': 'UDP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-1d4856299e9a5e9a` | `S1_llm_only` | `'has_cumulative_program_period'}` | {'label': '19/2030Z - 20/0359Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 19/2030Z - 20/0359Z |
| `cand-30a530cdd4403781` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. | `fact-41aee633f1048738` | `fact-41aee633f1048738` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. |
| `cand-35534c92fa450375` | `S1_llm_only` | `'has_staffing_comment'}` | {'label': 'BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45.'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | STAFFING COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. |
| `cand-3ad54f638dfbfe5b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T18:55:00Z | `fact-e623ff28b59f1131` | `fact-e623ff28b59f1131` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/19 18:55 |
| `cand-3e17fa7067cc122a` | `S2_llm_schema_slice` | `initiativeComments` | CDM GROUND DELAY PROGRAM; DELAY ASSIGNMENT MODE: UDP ARRIVALS; PROGRAM RATE: 28/28/28/24/20/20/20/20; MAXIMUM DELAY: 106; AVERAGE DELAY: 54. | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM ... DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0359Z ... PROGRAM RATE: 28/28/28/24/20/20/20/20... |
| `cand-3f3a643bc9b3d5d9` | `S2_llm_schema_slice` | `advisoryNumber` | 79 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-08-f6b3279e05f6` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/20... |
| `cand-480dfeb559e15aef` | `S1_llm_only` | `'has_average_delay_minutes'}` | {'label': '54'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 54 |
| `cand-5038b9a7bff28a78` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 79 | `fact-8bd80e06570f477d` | `fact-8bd80e06570f477d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM |
| `cand-53c5e8e9374262ee` | `S1_llm_only` | `'applies_to_scope'}` | {'label': 'ZME'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-6b7f6682d948e527` | `S1_llm_only` | `'delay_assignment_table_applies_to'}` | {'label': 'ZME'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZME |
| `cand-71a2222b358e93b4` | `S1_llm_only` | `'has_canadian_departure_arpts_included'}` | {'label': 'NONE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: NONE |
| `cand-7b67d7564a2016ca` | `S1_llm_only` | `'has_estimated_arrival_window'}` | {'label': '19/2030Z - 20/0359Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 19/2030Z - 20/0359Z |
| `cand-7be5c19b5dbc981f` | `S1_llm_only` | `'has_effective_time'}` | {'label': '191854-200459'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 191854-200459 |
| `cand-85861625749a804e` | `S1b_llm_canonicalized` | `impactingCondition` | staffing | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-8ce6d023803a538b` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-19T20:30:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-06-5aba4a79c09e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/20... |
| `cand-93190a84c993cc07` | `S1_llm_only` | `'has_program_rate_pattern'}` | {'label': '28/28/28/24/20/20/20/20'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 28/28/28/24/20/20/20/20 |
| `cand-948ef3dda162493a` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-20T03:59:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-07-435a7f2bd5ad` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/20... |
| `cand-96cd4dca724d9d67` | `S2_llm_schema_slice` | `controlledNASelement` | BNA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-01-d35d539ffd36` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS |
| `cand-aa6482cdd746e9d4` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-03-34f3e0560ca1` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/20... |
| `cand-b12c686ffe00e956` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-19T18:55:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-05-31918c40380e` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: BNA ELEMENT TYPE: APT ADL TIME: 1851Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 19/20... |
| `cand-b6ffe7a53594ad3c` | `S1_llm_only` | `'has_ctl_element'}` | {'label': 'APT ADL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: BNA ELEMENT TYPE: APT ADL |
| `cand-bdd7c0ef8b01d784` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:BNA | `fact-1c03d460c6dc269f` | `fact-1c03d460c6dc269f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: BNA |
| `cand-d9113b2c0b6c635d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-91382eed73503ca3` | `fact-91382eed73503ca3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-dd9f059e9b1e50cd` | `S2_llm_schema_slice` | `impactingConditionMessage` | BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-04-3c47a3a01a8e` | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. |
| `cand-df5cf76e1d879d57` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-017:fact-02-b0e71f29170b` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: BNA STAFFING TRIGGER. MODIFIED LOW POPUP. TIME + 45. |
| `cand-e282c6f21516fc7d` | `S1_llm_only` | `'includes_flights'}` | {'label': 'ALL CONTIGUOUS US DEP DEP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-e941f3b05eec80af` | `S1_llm_only` | `'has_impacting_condition'}` | {'label': 'STAFFING'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING |
| `cand-f69669631039ffc7` | `S0_rule_only` | `impactingCondition` | staffing | `fact-55ba0ebe57eb90f0` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-fa585d27da6a7b85` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T18:54:00Z | `fact-f691c97fd20bfad5` | `fact-f691c97fd20bfad5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 191854-200459 |
| `cand-fa9dd6ec63e979a6` | `S2_llm_schema_slice` | `departureScope` | ALL CONTIGUOUS US DEP | `` | `S2_llm_schema_slice:ATCSCC-GOLD-017:fact-02-de61c49b3e58` | `{"repaired_accepted": 1}` | `{}` | FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: NONE |

## ATCSCC-GOLD-020 / 2026-05-15:084

- Batch: `batch_02`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_02.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=71, est=22 min)
- Candidate class: `GroundDelayProgramTMI`
- Candidate clusters: 34
- Cross-system clusters: 33
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=84

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2254Z - 16/0659Z CUMULATIVE PROGRAM PERIOD: 15/1500Z - 16/0659Z PROGRAM RATE: 36/36/36/30/30/32/36/36/36 FLT INCL: ALL CONTIGUOUS US DEP DEP SCOPE: (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC DELAY ASSIGNMENT TABLE APPLIES TO: ZOA MAXIMUM DELAY: 758 AVERAGE DELAY: 70 IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER EFFECTIVE TIME: 15...

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-0c51c2646036b3c1` | `impactingCondition` | `allowed_value_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: STAFFING / STAFFING |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-0426b8b3461bc331` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-16T07:59:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-04-8e9bd86fc2f7` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |
| `cand-08d6f2796fd84e64` | `S3_llm_schema_slice_validator_repair` | `impactingConditionMessage` | STAFFING / STAFFING COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-07-939dee767a5f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |
| `cand-0a61768a28da2b0f` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-15T22:25:48Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-05-77b13b58d9e2` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |
| `cand-0a92cf8bc2ff779a` | `S1_llm_only` | `covers` | 15/2254Z - 16/0659Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVALS ESTIMATED FOR: 15/2254Z - 16/0659Z |
| `cand-0ed68aeb124eaf5c` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/2254Z - 16/0659Z CUMULATIVE PROG... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-08-29ce54083c2a` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |
| `cand-33bd087a51330433` | `S1_llm_only` | `has element type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-392e546f3baa6f10` | `S1_llm_only` | `is` | STAFFING | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER |
| `cand-3a028bed223067e3` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | {"@type": "nas:Airport", "evidence_text": "CTL ELEMENT: SFO ELEMENT TYPE: APT"} | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-02-6fb9416d2161` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO ELEMENT TYPE: APT |
| `cand-3a713bc3a3c78da8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `fact-ddb7bbb0b500d6f2` | `fact-ddb7bbb0b500d6f2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-3d5b154455f6cd26` | `S1_llm_only` | `includes` | CYEG CYVR CYYC | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC |
| `cand-43a31092946fdb20` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 84 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-01-8b0243478aff` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |
| `cand-5122dab5802bdade` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER | `fact-057bcfacfb154de3` | `fact-057bcfacfb154de3` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER |
| `cand-5791db8b75e0e2ef` | `S0_rule_only` | `impactingCondition` | staffing | `fact-0c51c2646036b3c1` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-69d1f8374abedb9c` | `S1_llm_only` | `covers` | 15/1500Z - 16/0659Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 15/1500Z - 16/0659Z |
| `cand-6b3b036e7354c7e2` | `S1_llm_only` | `is set to` | UDP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT MODE: UDP |
| `cand-6d4008cb9af0bb48` | `S3_llm_schema_slice_validator_repair` | `issuedTime` | 2026-05-15T23:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-09-2667384ec3b0` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |
| `cand-77db9d373b50988d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T23:00:00Z | `fact-68298fb3244b6dba` | `fact-68298fb3244b6dba` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 23:00 |
| `cand-7c186d82d4621337` | `S1_llm_only` | `lists` | 36/36/36/30/30/32/36/36/36 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROGRAM RATE: 36/36/36/30/30/32/36/36/36 |
| `cand-7c189d00568b2012` | `S1_llm_only` | `is stated as` | 2254Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ADL TIME: 2254Z |
| `cand-81eb43f66514f708` | `S1_llm_only` | `is identified as` | SFO | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-85f43bc2532116e3` | `S1_llm_only` | `is` | 70 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | AVERAGE DELAY: 70 |
| `cand-972a633df56acba4` | `S1_llm_only` | `announces` | CDM ground delay program | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-a81ab2fd430f1820` | `S1_llm_only` | `is` | 152258-160759 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 152258-160759 |
| `cand-a9c58bc609dfc1e7` | `S1_llm_only` | `includes` | ALL CONTIGUOUS US DEP DEP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | FLT INCL: ALL CONTIGUOUS US DEP DEP |
| `cand-ab99cd90298f562f` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-16T07:59:00Z | `fact-17f0c51679278139` | `fact-17f0c51679278139` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152258-160759 |
| `cand-b3db3929c6aecf02` | `S1_llm_only` | `applies to` | ZOA | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DELAY ASSIGNMENT TABLE APPLIES TO: ZOA |
| `cand-c5ce621832fff152` | `S1_llm_only` | `includes` | (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP SCOPE: (ALL+CZV_AP) ZLA ZAU ZLC ZTL ZDC ZNY ZHU ZJX ZFW ZOB ZDV ZOA ZSE ZBW ZMA ZKC ZME ZID ZAB ZMP |
| `cand-d0c837b43bfbc563` | `S1_llm_only` | `describe` | ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: STAFFING / STAFFING COMMENTS: ARR/DEP 28R/L, MODIFIED LOW POP UP, BY STATUS. PROCEDURAL COMPLICANCE ALSO A FACTOR WITH NCT STAFFING TRIGGER |
| `cand-dc03049d0083610c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingConditionMessage` | STAFFING / STAFFING | `fact-6aa5ea6b67bd998a` | `fact-6aa5ea6b67bd998a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: STAFFING / STAFFING |
| `cand-dc42f630b2d08dd3` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 84 | `fact-4f520381318e88b6` | `S1b_llm_canonicalized:2026-05-15:084:fact-152b12377aba, fact-4f520381318e88b6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM |
| `cand-ea57b9f0ceb00500` | `S1_llm_only` | `is` | 758 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | MAXIMUM DELAY: 758 |
| `cand-edd970c6de6735b8` | `S3_llm_schema_slice_validator_repair` | `impactingCondition` | other | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-06-e1af4bd4b509` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |
| `cand-f14315cfd8d4244b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T22:58:00Z | `fact-62b9f204d9304590` | `fact-62b9f204d9304590` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 152258-160759 |
| `cand-fccc52c14c0af763` | `S3_llm_schema_slice_validator_repair` | `departureScope` | {"atm:includesAirport": [{"@type": "nas:Airport", "evidence_text": "CANADIAN DEP ARPTS INCLUDED: CYEG CYVR CYYC"}], "atm:withinARTCC": [{... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-020:fact-03-8a9909745f35` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 2254Z DELAY ASSIGNMENT MODE: UDP ARRIVALS ESTIMATED FOR: 15/22... |

## ATCSCC-GOLD-055 / 2026-05-20:179

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=71, est=22 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 34
- Cross-system clusters: 33
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05202026&advn=179

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: PHL ELEMENT TYPE: APT ADL TIME: 2300Z GROUND STOP PERIOD: 20/2249Z - 21/0000Z DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 921 / 281 / 77 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: LACK OF ROUTES EFFECTIVE TIME: 202300-210100 SIGNATURE: 26/05/20 23:00 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-ed556e1da5cecefa` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-009cf140d19afb05` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-e757e732e9f10581` | `S2_llm_schema_slice:ATCSCC-GOLD-055:fact-03-af4c1ff278b2, fact-e757e732e9f10581` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-08c8f86acf8b0668` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-20T23:00:00Z | `fact-2dba4ebf3effb7a8` | `fact-2dba4ebf3effb7a8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202300-210100 |
| `cand-199ebb84311b4779` | `S2_llm_schema_slice` | `controlledNASelement` | PHL | `` | `S2_llm_schema_slice:ATCSCC-GOLD-055:fact-01-b82ad1778b1e` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: PHL ELEMENT TYPE: APT |
| `cand-1d9b3989e009a661` | `S1_llm_only` | `has_comment` | LACK OF ROUTES | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: LACK OF ROUTES |
| `cand-1ec51c6164ddb5c3` | `S3_llm_schema_slice_validator_repair` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZOB'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-1edf823c60aaff67` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-21T01:00:00Z | `fact-0599a351fd06b58d` | `fact-0599a351fd06b58d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 202300-210100 |
| `cand-2d0cfac18d11ed70` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-29ff48a6429cb5b8` | `S1b_llm_canonicalized:2026-05-20:179:fact-bcfe1e4b7526, S2_llm_schema_slice:ATCSCC-GOLD-055:fact-02-9c67cc46d01a, fact-29ff48a6429cb5b8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2efe9251b2500267` | `S1_llm_only` | `has_advisory_time` | 2300Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 2300Z |
| `cand-39e478306be1fa0f` | `S1_llm_only` | `has_ground_stop_period` | 20/2249Z - 21/0000Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 20/2249Z - 21/0000Z |
| `cand-42088cca6d66062e` | `S1_llm_only` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-46eca9c909123bb2` | `S1_llm_only` | `has_effective_time` | 202300-210100 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 202300-210100 |
| `cand-4745e7af87eb0764` | `S1_llm_only` | `has_advisory_identifier` | ADVZY 179 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-57bb51476af6a1d5` | `S1_llm_only` | `had_previous_total_maximum_average_delays` | 0 / 0 / 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-5d5b3681af37de1b` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PHL | `fact-f491602a52f403ea` | `S1b_llm_canonicalized:2026-05-20:179:fact-ec8b66969547, fact-f491602a52f403ea` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: PHL |
| `cand-5e9c11cfcc6aef47` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `initiativeComments` | LACK OF ROUTES | `fact-0c3911eccac1489d` | `S2_llm_schema_slice:ATCSCC-GOLD-055:fact-04-3d1d1b022a5b, fact-0c3911eccac1489d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | COMMENTS: LACK OF ROUTES |
| `cand-68952cd5a369c92d` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-6e2c29ed460292e5` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 179 | `fact-ec604c621010bf9a` | `S1b_llm_canonicalized:2026-05-20:179:fact-224bdff00c52, fact-ec604c621010bf9a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-6eecf8a9c22b4a39` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-ed556e1da5cecefa` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-7c4a0fe85ed605d6` | `S3_llm_schema_slice_validator_repair` | `controlledNASelement` | {'type': 'nas:Airport', 'value': 'PHL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL ELEMENT TYPE: APT |
| `cand-8af791243df59ffe` | `S1_llm_only` | `describes_flow_management_action` | GROUND STOP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `cand-94771a36dcbe1040` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-9769c11f8231dbc3` | `S3_llm_schema_slice_validator_repair` | `departureScope` | {'id': '_:depScope1', 'type': 'atm:AirportSpec'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-99dc74a2f9869180` | `S3_llm_schema_slice_validator_repair` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZID'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-9eb1adeb15113ffd` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-21T00:00:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-055:fact-07-8f1df9337e38` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2249Z - 21/0000Z |
| `cand-a1cd18f4b996a0d8` | `S1_llm_only` | `has_control_element` | PHL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: PHL |
| `cand-aa127eafa7a7d823` | `S1_llm_only` | `includes_departure_facilities` | ZDC ZOB ZID | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-d17f5917eca978aa` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-20T23:00:00Z | `fact-13d791423e385962` | `S2_llm_schema_slice:ATCSCC-GOLD-055:fact-05-1a78ab0bb836, fact-13d791423e385962` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/20 23:00 |
| `cand-dadd8bf98defe2b5` | `S1_llm_only` | `has_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-de315026b387dac3` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-e1fb2672284ec6a2` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-20T22:49:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-055:fact-06-4bb53f4c5363` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 20/2249Z - 21/0000Z |
| `cand-e39343247381d0e8` | `S1_llm_only` | `has_new_total_maximum_average_delays` | 921 / 281 / 77 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 921 / 281 / 77 |
| `cand-ef2ba2a4a60a39dc` | `S3_llm_schema_slice_validator_repair` | `includesAirport` | {'type': 'nas:Airport', 'value': 'ZDC'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-f73bebae5a44d6f7` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC ZOB ZID |
| `cand-fd160b9594124ef9` | `S1_llm_only` | `has_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-008 / 2026-05-17:019

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=69, est=22 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 33
- Cross-system clusters: 32
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05172026&advn=19

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL FOLLOW IF NECESSARY. SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES EFFECTIVE TIME: 171218-171645 SIGNATURE: 26/05/17 12:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-3ec3d540a86befa0` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-032f90fe7dacf76e` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-17T12:18:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-03-70d127852a71` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-04b4c63ca25d34cb` | `S1_llm_only` | `'arrival delays / airborne holding'}` | {'label': 'arrival delays and airborne holding', 'value': 'ARRIVAL DELAYS / AIRBORNE HOLDING'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-0cd464692e410cf2` | `S1_llm_only` | `'if necessary'}` | {'label': 'future updates', 'value': 'UPDATES'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-18cfe2c69d11db5b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SOUTH | `fact-1dad34599ec758cf` | `fact-1dad34599ec758cf` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-1c54f73133d57355` | `S1_llm_only` | `'arrival delays / airborne holding'}` | {'label': 'arrival delays and airborne holding', 'value': 'ARRIVAL DELAYS / AIRBORNE HOLDING'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UP TO 30 MINUTES DUE TO THUNDERSTORMS |
| `cand-1e1eaff26ce4b9c9` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SOUTH | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-27b791583ea5915d` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-17T12:18:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-02-de59ddf478fb` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-3720bc93f718ea2e` | `S1_llm_only` | `'up to 30 minutes'}` | {'label': 'delay duration', 'value': 'UP TO 30 MINUTES'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-3edf3c9c07ff5814` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:FLL | `` | `S1b_llm_canonicalized:2026-05-17:019:fact-f5042b890326` | `{"repaired_accepted": 1}` | `{}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-44cee5f9e12996db` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THE | `fact-67207f507bec2513` | `fact-67207f507bec2513` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-4bf34f910edf3e9a` | `S1_llm_only` | `'arrival delays'}` | {'label': 'South Florida airports', 'value': 'SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| `cand-4d0bcf4fa8e23773` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMA | `fact-3ec3d540a86befa0` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-5e2094d4220b3723` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-17T16:45:00Z | `fact-976e4c62b71d55f9` | `fact-976e4c62b71d55f9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171218-171645 |
| `cand-77e5b25b4e2f8b15` | `S1_llm_only` | `'South Florida airports'}` | {'label': 'South Florida airports', 'value': 'THE SOUTH FLORIDA AIRPORTS'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS |
| `cand-7c5f79007b5d369e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `fact-8cd7ba059d278acb` | `fact-8cd7ba059d278acb` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-801500c7f58618af` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:PBI | `` | `S1b_llm_canonicalized:2026-05-17:019:fact-5260dfc026bc` | `{"repaired_accepted": 1}` | `{}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-864aab1f1a580945` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:THEIR | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-8bb374499214d1c0` | `S2_llm_schema_slice` | `initiativeComments` | SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-06-614f27a83c5f` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-9c542e3fba3413bb` | `S2_llm_schema_slice` | `controlledNASelement` | FLL | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-09-b9650c74ad52` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-9de0cd6445571602` | `S3_llm_schema_slice_validator_repair` | `initiativeComments` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO THUNDERSTORMS. UPDATES WILL... | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES DUE TO... |
| `cand-aa85f35c5c6147b2` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-05-4be1f5a9a0ea` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-b80eea9e547c8542` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `fact-c809a564bc91bb8d` | `fact-c809a564bc91bb8d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |
| `cand-bf2b44e46daa419c` | `S2_llm_schema_slice` | `advisoryNumber` | 19 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-01-eaef48a3c1a2` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-c0cd6e01b50c5edf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-17T12:18:00Z | `fact-77181795d062dd22` | `fact-77181795d062dd22` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 171218-171645 |
| `cand-c3dffb3f22541108` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-17T16:45:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-04-f09924a718f6` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-cd716badd6aeb1e3` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 19 | `fact-c5825056cff79765` | `S1b_llm_canonicalized:2026-05-17:019:fact-1bf9c6e24677, fact-c5825056cff79765` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| `cand-d1c94018f9f4739c` | `S1_llm_only` | `'MIA, PBI, FLL and their satellites'}` | {'label': 'example airports and satellites', 'value': 'MIA, PBI, FLL AND THEIR SATELLITES'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-d3e8bb99475ab904` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:MIA | `` | `S1b_llm_canonicalized:2026-05-17:019:fact-cc2d0e052dfd` | `{"repaired_accepted": 1}` | `{}` | SOUTH FLORIDA AIRPORTS INCLUDE BUT ARE NOT LIMITED TO: MIA, PBI, FLL AND THEIR SATELLITES |
| `cand-ec4eda07e331fc6d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-17T12:18:00Z | `fact-fd7b321ff0fc4217` | `fact-fd7b321ff0fc4217` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/17 12:18 |
| `cand-ec7cb3d0943cc049` | `S2_llm_schema_slice` | `controlledNASelement` | PBI | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-08-91cdce6c6378` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-f3caf03d39285ad3` | `S2_llm_schema_slice` | `controlledNASelement` | MIA | `` | `S2_llm_schema_slice:ATCSCC-GOLD-008:fact-07-df28c705ab76` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS MESSAGE: EVENT TIME: 17/1215 - 17/1615 CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AI... |
| `cand-fcac0a97251ab71b` | `S1b_llm_canonicalized` | `impactingCondition` | arrival delays and airborne holding arrival delays / airborne holding | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | UP TO 30 MINUTES DUE TO THUNDERSTORMS |
| `cand-fd0683497e7e907a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `fact-8dde15af650cc694` | `fact-8dde15af650cc694` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZMA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO THE SOUTH FLORIDA AIRPORTS OF UP TO 30 MINUTES |

## ATCSCC-GOLD-031 / 2026-05-19:011

- Batch: `batch_04`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_04.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=69, est=22 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 33
- Cross-system clusters: 32
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05192026&advn=11

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: SFO ELEMENT TYPE: APT ADL TIME: 0409Z GROUND STOP PERIOD: 19/0400Z - 19/0515Z CUMULATIVE PROGRAM PERIOD: 18/1515Z - 19/0659Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 142 / 63 / 16 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 772 / 228 / 86 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: OTHER / OTHER COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. EFFECTIVE TIME: 190409-190615 SIGNATURE: 26/05/19 04:10 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-44048e5ecf75db1b` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: OTHER / OTHER |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-00d9022b39f54f7a` | `S1_llm_only` | `'is_impacted_by_condition'}` | {'class': 'impacting_condition', 'text': 'OTHER / OTHER'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-071caa168f08eef7` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | SFO | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-031:fact-01-2ded4d518efa` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: SFO |
| `cand-07665cf04747eedb` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-19T04:00:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-031:fact-06-613e43337c22` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 19/0400Z - 19/0515Z |
| `cand-0d402c4b2316fd1b` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZOA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE |
| `cand-0e325668358f8031` | `S1_llm_only` | `'applies_to_control_element'}` | {'class': 'facility', 'text': 'SFO'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: SFO |
| `cand-18c3fde70bbbfbfc` | `S1_llm_only` | `'has_probability_of_extension'}` | {'class': 'probability_level', 'text': 'MEDIUM'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-2202056734ee12b3` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE |
| `cand-27120cf6c72ddfde` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:APT | `` | `S1b_llm_canonicalized:2026-05-19:011:fact-51ca05f6a7eb` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-3633d5b2c8883dc9` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZSE | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE |
| `cand-367caffb196d2542` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-19T04:10:00Z | `fact-6d335b39d39da1e6` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-031:fact-05-aca393b74fd2, fact-6d335b39d39da1e6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/19 04:10 |
| `cand-407eb9e1c5b0f5a8` | `S1b_llm_canonicalized` | `impactingCondition` | due to procedural compliance and runway construction. | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-40973cf3ec88624b` | `S0_rule_only` | `impactingConditionMessage` | OTHER / OTHER | `fact-44048e5ecf75db1b` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-45a82f1214eea374` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | other | `fact-bd0efcc93d39fb9a` | `fact-bd0efcc93d39fb9a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER |
| `cand-47cd5986d8c6c657` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-19T04:09:00Z | `fact-c6647594e2773d37` | `fact-c6647594e2773d37` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190409-190615 |
| `cand-5adc0dbf7c5f4b90` | `S1_llm_only` | `'includes_departure_facilities'}` | {'class': 'facility_group', 'text': 'ZLA ZLC ZOA ZSE'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE |
| `cand-7036e6cb8c8a7bc6` | `S1_llm_only` | `'has_comment_explaining_cause'}` | {'class': 'comment', 'text': 'DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION.'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-7256427f233dd918` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZOA ZSE |
| `cand-72d2e1a43b675c68` | `S1_llm_only` | `'has_cumulative_program_period'}` | {'class': 'time_interval', 'text': '18/1515Z - 19/0659Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CUMULATIVE PROGRAM PERIOD: 18/1515Z - 19/0659Z |
| `cand-74840e2f736e16df` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADL | `` | `S1b_llm_canonicalized:2026-05-19:011:fact-5c26e921d6ae` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-785d5265f8bf87ed` | `S1_llm_only` | `'has_effective_time'}` | {'class': 'effective_time_interval', 'text': '190409-190615'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 190409-190615 |
| `cand-8a9153bb3f9911c2` | `S1_llm_only` | `'has_advisory_time'}` | {'class': 'zulu_time', 'text': '0409Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 0409Z |
| `cand-8bced49e66dcbadd` | `S1_llm_only` | `'announces'}` | {'class': 'traffic_management_program', 'text': 'GROUND STOP'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP |
| `cand-8cb93377221510d4` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | other | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-031:fact-03-788694e04537` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: OTHER / OTHER COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-92667605cfd166b5` | `S0_rule_only, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. | `fact-68041c421f8553fe` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-031:fact-04-3f94f4dc5e3f, fact-68041c421f8553fe` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | COMMENTS: DUE TO PROCEDURAL COMPLIANCE AND RUNWAY CONSTRUCTION. |
| `cand-964d9c1174043e81` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SFO | `fact-bd94620f3f6aa281` | `S1b_llm_canonicalized:2026-05-19:011:fact-5b234cfd8d01, fact-bd94620f3f6aa281` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: SFO |
| `cand-b84d1374a2084688` | `S1_llm_only` | `'has_control_element_type'}` | {'class': 'control_element_type', 'text': 'APT ADL'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-bc3ea3660469da1b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-19T06:15:00Z | `fact-38fa092321fc129f` | `fact-38fa092321fc129f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 190409-190615 |
| `cand-ca6448ab68c57e4c` | `S1_llm_only` | `'previous_delays_reported_as'}` | {'class': 'delay_statistics', 'text': '142 / 63 / 16'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 142 / 63 / 16 |
| `cand-e649736ac9016213` | `S0_rule_only, S1b_llm_canonicalized, S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-d661b42a1554f7e9` | `S1b_llm_canonicalized:2026-05-19:011:fact-bcfe1e4b7526, S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-031:fact-02-a322855bd01f, fact-d661b42a1554f7e9` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-eb5072224f11009a` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 11 | `fact-08b650db05198fff` | `S1b_llm_canonicalized:2026-05-19:011:fact-5953529e03c9, fact-08b650db05198fff` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP |
| `cand-f4d0ff77d4bcb858` | `S1_llm_only` | `'has_ground_stop_period'}` | {'class': 'time_interval', 'text': '19/0400Z - 19/0515Z'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 19/0400Z - 19/0515Z |
| `cand-fc75b7f858bb50cc` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-19T05:15:00Z | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-031:fact-07-5546082945e2` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 19/0400Z - 19/0515Z |
| `cand-fe4446968cc8182c` | `S1_llm_only` | `'new_delays_reported_as'}` | {'class': 'delay_statistics', 'text': '772 / 228 / 86'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 772 / 228 / 86 |

## ATCSCC-GOLD-053 / 2026-05-18:125

- Batch: `batch_06`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_06.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `heavy` (score=67, est=21 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 32
- Cross-system clusters: 31
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=125

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 125 STL/ZKC 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2025Z GROUND STOP PERIOD: 18/1929Z - 18/2130Z DEP FACILITIES INCLUDED: (Manual) ZID PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-5951209b4fb2145a` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03986f72084148c2` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZID | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZID |
| `cand-0cac4baf1773ea3a` | `S2_llm_schema_slice` | `controlledNASelement` | STL | `` | `S2_llm_schema_slice:ATCSCC-GOLD-053:fact-01-c76ace5f8042` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: STL ELEMENT TYPE: APT ADL TIME: 2025Z GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-12099287d9982e9d` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-5f108c7322eafce7` | `S1b_llm_canonicalized:2026-05-18:125:fact-bcfe1e4b7526, S2_llm_schema_slice:ATCSCC-GOLD-053:fact-02-32d167cff862, fact-5f108c7322eafce7` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-13858ddd9823ea9c` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T20:30:00Z | `fact-cfb88e0abbcfb391` | `S2_llm_schema_slice:ATCSCC-GOLD-053:fact-04-def3d6665772, fact-cfb88e0abbcfb391` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | SIGNATURE: 26/05/18 20:30 |
| `cand-36d68ea181448c8a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-744ca4db1722c835` | `fact-744ca4db1722c835` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 182029-182230 SIGNATURE: 26/05/18 20:30 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-3d5cf236e640fafa` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-5951209b4fb2145a` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-3f9d8ad2f6135324` | `S1_llm_only` | `signature_time` | 26/05/18 20:30 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 20:30 |
| `cand-4681fcd07240e331` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 125 | `fact-9bc758f6f69d08de` | `fact-9bc758f6f69d08de` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 125 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `cand-47ded313bc0738c2` | `S1_llm_only` | `has_effective_time` | 182029-182230 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182029-182230 |
| `cand-4d49f6aa2522b0c7` | `S1_llm_only` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-4f8a5971c4ac583d` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-507d58fab93a01a4` | `S1_llm_only` | `declares_ground_stop_period` | 18/1929Z - 18/2130Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-598f5f1f2bf46941` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T22:30:00Z | `fact-a6809973278afd92` | `fact-a6809973278afd92` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-5aa66f87b45ab81f` | `S1_llm_only` | `includes_departure_facilities` | ZID | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZID |
| `cand-5bcab9f476aacc6e` | `S1_llm_only` | `has_time_label` | 2025Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | TIME: 2025Z |
| `cand-5f5c1918787f07f6` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:APT | `` | `S1b_llm_canonicalized:2026-05-18:125:fact-51ca05f6a7eb` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-75dca5e5aa1660e5` | `S1_llm_only` | `has_control_element` | STL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: STL |
| `cand-7cedaf791bbfe809` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T20:29:00Z | `fact-9636b890e9386958` | `fact-9636b890e9386958` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-81276727aac4f908` | `S1_llm_only` | `has_new_maximum_delay` | 267 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-820a7ec44a436d6e` | `S1_llm_only` | `has_previous_total_delays` | 927 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-86cdb0dabd9ff12f` | `S1_llm_only` | `has_control_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-89500a8108cb55f3` | `S2_llm_schema_slice` | `initiativeComments` | EFFECTIVE TIME: 182029-182230 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-053:fact-07-a08aec50bde1` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182029-182230 |
| `cand-8d82be281b171f4b` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:STL | `fact-8a438f1f97d02070` | `S1b_llm_canonicalized:2026-05-18:125:fact-ded7ffe6f47b, fact-8a438f1f97d02070` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: STL |
| `cand-91395b74551e1b73` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T21:30:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-053:fact-06-2576328eda6a` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-9afb3e39353440a0` | `S1_llm_only` | `has_new_average_delay` | 175 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-a9cadccb7f072a70` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-2f4723bab70428df` | `S2_llm_schema_slice:ATCSCC-GOLD-053:fact-03-3f694c145870, fact-2f4723bab70428df` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-ba24b7ba081a99dd` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T19:29:00Z | `` | `S2_llm_schema_slice:ATCSCC-GOLD-053:fact-05-52dcdcc176d1` | `{"repaired_accepted": 1}` | `{}` | GROUND STOP PERIOD: 18/1929Z - 18/2130Z |
| `cand-dbd1d250aae72e01` | `S1_llm_only` | `has_new_total_delays` | 1403 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1403 / 267 / 175 |
| `cand-e530aa02c3e4fee4` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ADL | `` | `S1b_llm_canonicalized:2026-05-18:125:fact-5c26e921d6ae` | `{"repaired_accepted": 1}` | `{}` | ELEMENT TYPE: APT ADL |
| `cand-e8bb8937efa64e10` | `S1_llm_only` | `has_previous_maximum_delay` | 211 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-ee0be780043e9faa` | `S1_llm_only` | `has_previous_average_delay` | 116 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 927 / 211 / 116 |
| `cand-eec142cf318a3025` | `S1_llm_only` | `has_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |

## ATCSCC-GOLD-025 / 2026-05-18:144

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `medium` (score=65, est=20 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 31
- Cross-system clusters: 30
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=144

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DTW ELEMENT TYPE: APT ADL TIME: 2208Z GROUND STOP PERIOD: 18/2126Z - 18/2245Z DEP FACILITIES INCLUDED: (Manual) ZDC PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: ZID REMOVED FROM STOP. EFFECTIVE TIME: 182212-182345 SIGNATURE: 26/05/18 22:13 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-1d7ce7af4a29c5bd` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-09b4e474a08d2632` | `S2_llm_schema_slice` | `controlledNASelement` | nas:Airport(DTW) | `` | `S2_llm_schema_slice:ATCSCC-GOLD-025:fact-01-9a8825a69534` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DTW ELEMENT TYPE: APT |
| `cand-109f1b3288d9b43b` | `S2_llm_schema_slice` | `advisoryNumber` | 144 | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |
| `cand-1b46f0fc77e40c48` | `S1_llm_only` | `identifies_controlled_element` | DTW | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DTW |
| `cand-2076ca069a700c2a` | `S1_llm_only` | `sets_ground_stop_period` | 18/2126Z - 18/2245Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 18/2126Z - 18/2245Z |
| `cand-23c2e603017cc75e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T23:45:00Z | `fact-0c32b995f08fccba` | `fact-0c32b995f08fccba` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182212-182345 |
| `cand-3390a1931b681bff` | `S1_llm_only` | `reports_new_delays` | 0 / 0 / 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-347ce50cf6ec3f4c` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | ZID REMOVED FROM STOP. | `fact-c37edf02b7c379e2` | `fact-c37edf02b7c379e2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-5114e03377deefe8` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DTW | `fact-cccabb0782b3954b` | `fact-cccabb0782b3954b` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CTL ELEMENT: DTW |
| `cand-5f5bf120ae1892ea` | `S1_llm_only` | `states_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ELEMENT TYPE: APT ADL |
| `cand-5f9916fb2606922c` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-18T22:12:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-73dd866057e92a76` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-18T22:34:59Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-8a25a93040e32551` | `S1_llm_only` | `provides_effective_time` | 182212-182345 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 182212-182345 |
| `cand-8a4d52f755f8c978` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-cae9b520247de872` | `fact-cae9b520247de872` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-8a75557726aa8f37` | `S2_llm_schema_slice` | `initiativeComments` | ZID REMOVED FROM STOP. | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-8dec8fee8da6181e` | `S1_llm_only` | `notes_comment` | ZID REMOVED FROM STOP. | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | COMMENTS: ZID REMOVED FROM STOP. |
| `cand-bfec83f04decf738` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC |
| `cand-c216895a26fcfe92` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T22:12:00Z | `fact-19bfbd21d235ba00` | `fact-19bfbd21d235ba00` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 182212-182345 |
| `cand-ccac8eeb004983d2` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d505bc80452fd4f0` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-1d7ce7af4a29c5bd` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d63611218fb40e69` | `S1_llm_only` | `states_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-d73d6d85232e9199` | `S1_llm_only` | `reports_previous_delays` | 0 / 0 / 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-db8d40f4b0469e9d` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T22:13:00Z | `fact-e3a0b47c530ee23a` | `fact-e3a0b47c530ee23a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 22:13 |
| `cand-dd7fe42d7e0aa23e` | `S2_llm_schema_slice` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-e13c0603b93a6dca` | `S2_llm_schema_slice` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e94505a05e34b884` | `S1_llm_only` | `includes_departure_facility` | ZDC | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (Manual) ZDC |
| `cand-ea5d486ab82989ee` | `S1_llm_only` | `identifies_impacting_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-edfbd49206f32355` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-dd49f31aefd62517` | `S1b_llm_canonicalized:2026-05-18:144:fact-bcfe1e4b7526, fact-dd49f31aefd62517` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-ee43b07de6fb2501` | `S1_llm_only` | `has_signature_time` | 26/05/18 22:13 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 22:13 |
| `cand-f73d13eae3bcbe7a` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-18T22:13:00Z | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1}` | SIGNATURE: 26/05/18 22:13 |
| `cand-fb2740f204293e4b` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 144 | `fact-60467ef83265dd3a` | `S1b_llm_canonicalized:2026-05-18:144:fact-4d23ca1c7a8e, fact-60467ef83265dd3a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |
| `cand-fc58c344eb3e64c8` | `S1_llm_only` | `states_action` | GROUND STOP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |

## ATCSCC-GOLD-029 / 2026-05-18:001

- Batch: `batch_03`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_03.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `medium` (score=65, est=20 min)
- Candidate class: `GroundStopTMI`
- Candidate clusters: 31
- Cross-system clusters: 30
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=1

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP MESSAGE: CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 0000Z GROUND STOP PERIOD: 17/2350Z - 18/0115Z DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1793 / 77 / 47 PROBABILITY OF EXTENSION: MEDIUM IMPACTING CONDITION: WEATHER / THUNDERSTORMS COMMENTS: EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-6a0afb58dd53a055` | `impactingConditionMessage` | `domain_violation` | `nasa_atmonto_profile_gap_candidate` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03906a641a66bfc0` | `S0_rule_only` | `impactingConditionMessage` | WEATHER / THUNDERSTORMS | `fact-6a0afb58dd53a055` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-087d2dff925e74e2` | `S1_llm_only` | `previous_total_maximum_average_delays` | 0 / 0 / 0 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PREVIOUS TOTAL, MAXIMUM, AVERAGE DELAYS: 0 / 0 / 0 |
| `cand-0b503db0142a4e20` | `S1_llm_only` | `has_ground_stop_period` | 17/2350Z - 18/0115Z | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | GROUND STOP PERIOD: 17/2350Z - 18/0115Z |
| `cand-1f5a91f5ef87fa7e` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T00:02:00Z | `fact-1133b98417011f15` | `fact-1133b98417011f15` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 00:02 |
| `cand-2583ed8c700d85d6` | `S1_llm_only` | `new_total_maximum_average_delays` | 1793 / 77 / 47 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | NEW TOTAL, MAXIMUM, AVERAGE DELAYS: 1793 / 77 / 47 |
| `cand-27ee881772496010` | `S1_llm_only` | `has_advisory_type` | CDM GROUND STOP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP |
| `cand-302828c09cfd87cf` | `S1_llm_only` | `signed_at` | 26/05/18 00:02 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | SIGNATURE: 26/05/18 00:02 |
| `cand-4b1dc8db01f4aca3` | `S1b_llm_canonicalized` | `impactingCondition` | weather / thunderstorms | `` | `` | `{"rejected_schema": 1}` | `{"allowed_value_violation": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-52d08d9789919b18` | `S1_llm_only` | `includes_departure_facilities` | ZLA ZLC ZDV ZKC ZAB ZMP | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-57c3d0c16e1edbf4` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DEN | `fact-0f47acb137a5314d` | `S1b_llm_canonicalized:2026-05-18:001:fact-9218607e89ff, fact-0f47acb137a5314d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | CTL ELEMENT: DEN |
| `cand-6b87441ef700d2f5` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T02:15:00Z | `fact-d3a2f3274a311a52` | `S2_llm_schema_slice:ATCSCC-GOLD-029:fact-05-bc01782bf937, fact-d3a2f3274a311a52` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 180001-180215 |
| `cand-77a9d030b4a33bf8` | `S1_llm_only` | `names_control_element` | DEN | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN |
| `cand-7b897dd94631fa93` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `extensionProbability` | MEDIUM | `fact-68e383919dbd392d` | `S1b_llm_canonicalized:2026-05-18:001:fact-bcfe1e4b7526, S2_llm_schema_slice:ATCSCC-GOLD-029:fact-02-209e8af915a9, fact-68e383919dbd392d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-7fdbf3949f6ad104` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-81a8c3284f54564c` | `S1_llm_only` | `has_impacting_condition` | WEATHER / THUNDERSTORMS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-82d92daa500dd87a` | `S3_llm_schema_slice_validator_repair` | `extensionProbability` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-99e502e47d1f7724` | `S2_llm_schema_slice` | `controlledNASelement` | DEN | `` | `S2_llm_schema_slice:ATCSCC-GOLD-029:fact-01-2c5298f63ca7` | `{"repaired_accepted": 1}` | `{}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL TIME: 0000Z GROUND STOP PERIOD: 17/2350Z - 18/0115Z |
| `cand-a0ae6e8e06bdbabe` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZDV | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-a15e670301cc7cb8` | `S1_llm_only` | `has_probability_of_extension` | MEDIUM | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | PROBABILITY OF EXTENSION: MEDIUM |
| `cand-a4050da616e33f89` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `initiativeComments` | EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Vie... | `fact-7380abf84e750f3d` | `fact-7380abf84e750f3d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | COMMENTS: EFFECTIVE TIME: 180001-180215 SIGNATURE: 26/05/18 00:02 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Vie... |
| `cand-ad8753f855e364bb` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T00:01:00Z | `fact-d764204ad499c4f5` | `S2_llm_schema_slice:ATCSCC-GOLD-029:fact-04-f50a144afb63, fact-d764204ad499c4f5` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | EFFECTIVE TIME: 180001-180215 |
| `cand-b0b2dd035a2cf4d7` | `S1_llm_only` | `has_effective_time` | 180001-180215 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 180001-180215 |
| `cand-be3cfeb5ed29bab8` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZMP | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-be62ff5679e50508` | `S2_llm_schema_slice` | `initiativeComments` | THUNDERSTORMS | `` | `S2_llm_schema_slice:ATCSCC-GOLD-029:fact-06-551595b4d821` | `{"repaired_accepted": 1}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d1f9166abf80ecdc` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZAB | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-d2462e37990fb2e5` | `S3_llm_schema_slice_validator_repair` | `impactingCondition` | weather | `` | `` | `{"rejected_schema": 1}` | `{"predicate_not_object_property": 1, "unknown_object_class": 1, "unknown_subject_class": 1}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-d34cc52d495205f8` | `S0_rule_only, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `impactingCondition` | weather | `fact-2f0d9e885239743f` | `S2_llm_schema_slice:ATCSCC-GOLD-029:fact-03-3435d55630e8, fact-2f0d9e885239743f` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | IMPACTING CONDITION: WEATHER / THUNDERSTORMS |
| `cand-e71580455a091361` | `S1_llm_only` | `has_element_type` | APT ADL | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | CTL ELEMENT: DEN ELEMENT TYPE: APT ADL |
| `cand-fa083e6267f69373` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZKC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |
| `cand-fc661d8b2523dc14` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 1 | `fact-f0580621a44d3ecc` | `S1b_llm_canonicalized:2026-05-18:001:fact-370049e1a6bc, fact-f0580621a44d3ecc` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP |
| `cand-fdbc5707b13a794f` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLC | `` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | DEP FACILITIES INCLUDED: (1stTier) ZLA ZLC ZDV ZKC ZAB ZMP |

## ATCSCC-GOLD-002 / 2026-05-15:063

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `medium` (score=61, est=19 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 29
- Cross-system clusters: 28
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05152026&advn=63

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 15/1918 - 16/0000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 151918-160030 SIGNATURE: 26/05/15 19:18 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-3829fb605fdc838b` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-03d2b704d6be0b1c` | `S1_llm_only` | `can_expect` | airborne holding into San Diego Airport | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT |
| `cand-161d19bb2457224a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `fact-9937cf1feef86807` | `fact-9937cf1feef86807` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-2a48e7bbcc59050a` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-15T19:18:00Z | `fact-667e954adb4485df` | `fact-667e954adb4485df` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-2cd6d1eb74d6c128` | `S1_llm_only` | `are_due_to` | compacted demand | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-31061102a9a4c8ce` | `S1_llm_only` | `can_expect` | arrival delays | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT |
| `cand-33d28dbc7c892558` | `S3_llm_schema_slice_validator_repair` | `effectiveEndTime` | 2026-05-16T00:00:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-002:fact-03-56010ee7457b` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-3672d79202199bb9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-15T19:18:00Z | `fact-0a7cb6a4552e94b2` | `fact-0a7cb6a4552e94b2` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 19:18 |
| `cand-480627a568804dc1` | `S2_llm_schema_slice` | `extensionProbability` | LOW | `` | `S2_llm_schema_slice:ATCSCC-GOLD-002:fact-07-81c2c1d35072` | `{"repaired_accepted": 1}` | `{}` | UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-4b0313b23f63448b` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `fact-ff0d97c756b59437` | `fact-ff0d97c756b59437` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-62104fae3fc48981` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `fact-3829fb605fdc838b` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-765670f6e4fa2213` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-16T00:30:00Z | `fact-71281d2fd7ed361a` | `fact-71281d2fd7ed361a` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-81dac5edcd117771` | `S3_llm_schema_slice_validator_repair` | `advisoryNumber` | 63 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-002:fact-01-881947fdf99d` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-872a90f29c295367` | `S3_llm_schema_slice_validator_repair` | `effectiveStartTime` | 2026-05-15T19:18:00 | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-002:fact-02-c5f1bac690eb` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-875ea39dcff9a520` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `initiativeComments` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL F... | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-002:fact-06-50a2c28a7c74` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. |
| `cand-8b24911961d6ec51` | `S2_llm_schema_slice` | `issuedTime` | 2026-05-15T19:18:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-002:fact-02-cb6b08cf1d3c` | `{"repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/15 19:18 |
| `cand-91e158e08a15dbda` | `S2_llm_schema_slice` | `effectiveStartTime` | 2026-05-15T19:18:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-002:fact-03-bbe57c10cce7` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-b3ef4114981bc2fd` | `S2_llm_schema_slice` | `controlledNASelement` | San Diego Airport | `` | `S2_llm_schema_slice:ATCSCC-GOLD-002:fact-06-1bd1ad66b698` | `{"repaired_accepted": 1}` | `{}` | USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-b45d13444bd57cc8` | `S1_llm_only` | `have_maximum_duration` | up to 30 minutes | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-b4f391faf4ce0c38` | `S1_llm_only` | `announces` | SAN airport arrival delays | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-cbe6cb9e8f529674` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:SAN | `fact-7b80c928ec3e7782` | `fact-7b80c928ec3e7782` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-d99125d7e166cbff` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `impactingCondition` | volume | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-002:fact-05-890df6317ea6` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-dcfd8a9f849d6e78` | `S3_llm_schema_slice_validator_repair, S4_hybrid_backbone_enrichment` | `controlledNASelement` | SAN Airport | `` | `S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-002:fact-04-ac0feb8d915c` | `{"hybrid_enrichment_accepted": 1, "repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-e2a1b014664055e9` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:DIEGO | `fact-623b32490b71dea4` | `fact-623b32490b71dea4` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-e33d82cdf5f8ea54` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `fact-b670ee084565cf3d` | `fact-b670ee084565cf3d` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES |
| `cand-e517d0ce120e6c3e` | `S0_rule_only, S1b_llm_canonicalized, S2_llm_schema_slice, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 63 | `fact-0e4150ba287b63bd` | `S1b_llm_canonicalized:2026-05-15:063:fact-769d2b922a34, S2_llm_schema_slice:ATCSCC-GOLD-002:fact-01-7e38d7c0f984, fact-0e4150ba287b63bd` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 3}` | `{}` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `cand-e5a671e3e01f06a8` | `S1_llm_only` | `has_time_span` | 15/1918 - 16/0000 | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 15/1918 - 16/0000 |
| `cand-ec55bc9996a5e532` | `S2_llm_schema_slice` | `initiativeComments` | Users can expect arrival delays / airborne holding into San Diego Airport of up to 30 minutes due to compacted demand. Updates will follo... | `` | `S2_llm_schema_slice:ATCSCC-GOLD-002:fact-05-8a846d07b0b5` | `{"repaired_accepted": 1}` | `{}` | MESSAGE: EVENT TIME: 15/1918 - 16/0000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO SAN DIEGO AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED... |
| `cand-f179f8ec46ba0510` | `S2_llm_schema_slice` | `effectiveEndTime` | 2026-05-16T00:30:00 | `` | `S2_llm_schema_slice:ATCSCC-GOLD-002:fact-04-f6cdd217bfec` | `{"repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 151918-160030 |
| `cand-f44ec5879948c238` | `S1_llm_only` | `will_follow_if_necessary` | True | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |

## ATCSCC-GOLD-003 / 2026-05-18:069

- Batch: `batch_01`
- Decision template: `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
- Batch checklist: `data/evaluation/nasa_atmonto/review_batches/batch_01.md`
- Priority lane: `1_rejection_adjudication`
- Complexity: `medium` (score=51, est=16 min)
- Candidate class: `TrafficManagementInitiative`
- Candidate clusters: 24
- Cross-system clusters: 23
- Rejected facts: 1
- Source URL: https://www.fly.faa.gov/adv/adv_otherdis?adv_date=05182026&advn=69

Source excerpt:

> ATCSCC Advisory FAA Home Air Traffic Control System Command Center ATCSCC Home \| Products \| What's New \| Site Map \| ATCSCC FAQ \| Diversion Forums \| Text-Only Version ATCSCC Advisory ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS MESSAGE: EVENT TIME: 18/1545 - 18/2000 CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED DEMAND. UPDATES WILL FOLLOW IF NECESSARY. EFFECTIVE TIME: 181545-182030 SIGNATURE: 26/05/18 15:45 FAA.gov Home \| Privacy Policy \| Web Policies & Notices \| Contact Us Readers & Viewers: PDF Reader \| MS Word Viewer \| MS PowerPoint Viewer \| MS Excel Viewer \| WinZip

Rejected facts to adjudicate:

| Fact ID | Predicate | Errors | Suggested decision | Evidence |
| --- | --- | --- | --- | --- |
| `fact-3fdded79d37c7ffe` | `controlledNASelement` | `range_violation` | `nasa_atmonto_profile_gap_candidate` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |

Candidate clusters:

| Candidate | Systems | Predicate | Value/Object | S0 IDs | Schema-valid S1-S3 IDs | Validator | Errors | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cand-120cdf0b1c721a94` | `S0_rule_only` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:ZLA | `fact-3fdded79d37c7ffe` | `` | `{"rejected_schema": 1}` | `{"range_violation": 1}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-1c20a51d704da888` | `S1_llm_only` | `'can_expect_arrival_delays_or_airborne_holding'}` | {'type': 'delay_duration', 'value': 'up to 30 minutes'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-1e26b75fad279cbf` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `fact-20c5df06077d10e6` | `fact-20c5df06077d10e6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-2a7d43ffe301b8fc` | `S1_llm_only` | `'caused_by'}` | {'type': 'demand_condition', 'value': 'compacted demand'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | DUE TO COMPACTED DEMAND |
| `cand-38785d11ab0ada24` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveStartTime` | 2026-05-18T15:45:00Z | `fact-a4e944e97d37d1d4` | `fact-a4e944e97d37d1d4` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181545-182030 |
| `cand-4760f2ad6956d861` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `effectiveEndTime` | 2026-05-18T20:30:00Z | `fact-8e728eaeb708e3ae` | `fact-8e728eaeb708e3ae` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | EFFECTIVE TIME: 181545-182030 |
| `cand-4ed4d7dac9c4fde3` | `S2_llm_schema_slice` | `impactingCondition` | volume | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED... |
| `cand-57de26e503671d37` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:LAS | `` | `S1b_llm_canonicalized:2026-05-18:069:fact-ed15a8e07bf4` | `{"repaired_accepted": 1}` | `{}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-618359e579b914f6` | `S2_llm_schema_slice` | `advisoryNumber` | 69 | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED... |
| `cand-70163bcbdf393132` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:USERS | `fact-020653628356973c` | `fact-020653628356973c` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-7716781deb55b778` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:CAN | `fact-394cd35e1a730575` | `fact-394cd35e1a730575` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-7a26d7e447f9e5fb` | `S2_llm_schema_slice` | `controlledNASelement` | LAS Vegas Airport | `` | `` | `{"rejected_evidence": 1}` | `{"evidence_not_found_in_source": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS ... USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES DUE TO COMPACTED... |
| `cand-7c2f15b6de0c86cf` | `S1_llm_only` | `'runs_to'}` | {'type': 'timestamp', 'value': '18/2000'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1545 - 18/2000 |
| `cand-7ec71a9c623357bd` | `S1b_llm_canonicalized` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:VEGAS | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-8c05d0dab8abcd27` | `S1b_llm_canonicalized` | `impactingCondition` | compacted demand demand_condition | `` | `` | `{"rejected_schema": 1}` | `{"domain_violation": 1}` | DUE TO COMPACTED DEMAND |
| `cand-8fa6b710bd1d5da8` | `S0_rule_only, S1b_llm_canonicalized, S4_hybrid_backbone_enrichment` | `advisoryNumber` | 69 | `fact-3f0ecd7cc04a59a8` | `S1b_llm_canonicalized:2026-05-18:069:fact-4d09d282f93b, fact-3f0ecd7cc04a59a8` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 2}` | `{}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-94d9fa191e3139b0` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:VEGAS | `fact-301c1191a4ac3c80` | `fact-301c1191a4ac3c80` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-95d49a54ce077cd4` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `issuedTime` | 2026-05-18T15:45:00Z | `fact-edb032e8d07ba6b6` | `fact-edb032e8d07ba6b6` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | SIGNATURE: 26/05/18 15:45 |
| `cand-9c2113d012bc7d9d` | `S1_llm_only` | `'runs_from'}` | {'type': 'timestamp', 'value': '18/1545'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EVENT TIME: 18/1545 - 18/2000 |
| `cand-aa1999464457c499` | `S1_llm_only` | `'announces_airport_arrival_delays'}` | {'type': 'airport', 'value': 'Las Vegas Airport'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `cand-ae202e6c578cf9f7` | `S0_rule_only, S4_hybrid_backbone_enrichment` | `controlledNASelement` | urn:aviation-agentic-ai:nas-element:INTO | `fact-7205c395ef835e6e` | `fact-7205c395ef835e6e` | `{"hybrid_backbone_accepted": 1, "repaired_accepted": 1}` | `{}` | CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS / AIRBORNE HOLDING INTO LAS VEGAS AIRPORT OF UP TO 30 MINUTES |
| `cand-bcda714224529b46` | `S1_llm_only` | `'promises_follow_up_updates_if_necessary'}` | {'type': 'update_notice', 'value': 'updates'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | UPDATES WILL FOLLOW IF NECESSARY |
| `cand-c9b58e4bd35b66f9` | `S1_llm_only` | `'ends_at'}` | {'type': 'timestamp', 'value': '182030'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181545-182030 |
| `cand-fcf62c6b906576d7` | `S1_llm_only` | `'starts_at'}` | {'type': 'timestamp', 'value': '181545'} | `` | `` | `{"rejected_schema": 1}` | `{"unknown_object_class": 1, "unknown_predicate": 1, "unknown_subject_class": 1}` | EFFECTIVE TIME: 181545-182030 |
