# NASA ATMONTO Cross-System Candidate Review

- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Candidate review JSONL: `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.jsonl`
- Records: 100
- Candidate clusters: 3169
- Raw fact counts by system: `{"S0_rule_only": 615, "S1_llm_only": 1211, "S1b_llm_canonicalized": 454, "S2_llm_schema_slice": 708, "S3_llm_schema_slice_validator_repair": 396, "S4_hybrid_backbone_enrichment": 686}`
- Cluster counts by system: `{"S0_rule_only": 609, "S1_llm_only": 1209, "S1b_llm_canonicalized": 454, "S2_llm_schema_slice": 703, "S3_llm_schema_slice_validator_repair": 396, "S4_hybrid_backbone_enrichment": 685}`
- Candidate kinds: `{"canonical_fact": 3126, "freeform_or_unmapped_fact": 40, "property_bundle": 3}`

## Completion Gate

- Use this cross-system candidate package during manual gold review so S1-S3 facts are considered alongside the rule-only baseline. It is not itself reviewed gold and must not be scored as manual truth.

## Review Queue

| Sample | Source | Class | Candidate clusters | Status |
| --- | --- | --- | ---: | --- |
| `ATCSCC-GOLD-001` | `2026-05-19:032` | `ReRouteTMI` | 35 | `reviewed` |
| `ATCSCC-GOLD-002` | `2026-05-15:063` | `TrafficManagementInitiative` | 29 | `reviewed` |
| `ATCSCC-GOLD-003` | `2026-05-18:069` | `TrafficManagementInitiative` | 24 | `reviewed` |
| `ATCSCC-GOLD-004` | `2026-05-14:059` | `TrafficManagementInitiative` | 36 | `reviewed` |
| `ATCSCC-GOLD-005` | `2026-05-19:059` | `TrafficManagementInitiative` | 32 | `reviewed` |
| `ATCSCC-GOLD-006` | `2026-05-19:144` | `GroundDelayProgramTMI` | 24 | `reviewed` |
| `ATCSCC-GOLD-007` | `2026-05-16:051` | `TrafficManagementInitiative` | 24 | `reviewed` |
| `ATCSCC-GOLD-008` | `2026-05-17:019` | `TrafficManagementInitiative` | 33 | `reviewed` |
| `ATCSCC-GOLD-009` | `2026-05-20:040` | `ReRouteTMI` | 38 | `reviewed` |
| `ATCSCC-GOLD-010` | `2026-05-20:053` | `ReRouteTMI` | 46 | `reviewed` |
| `ATCSCC-GOLD-011` | `2026-05-19:108` | `ReRouteTMI` | 45 | `reviewed` |
| `ATCSCC-GOLD-012` | `2026-05-18:053` | `ReRouteTMI` | 41 | `reviewed` |
| `ATCSCC-GOLD-013` | `2026-05-18:124` | `ReRouteTMI` | 39 | `reviewed` |
| `ATCSCC-GOLD-014` | `2026-05-18:104` | `ReRouteTMI` | 46 | `reviewed` |
| `ATCSCC-GOLD-015` | `2026-05-20:137` | `ReRouteTMI` | 37 | `reviewed` |
| `ATCSCC-GOLD-016` | `2026-05-20:078` | `ReRouteTMI` | 38 | `reviewed` |
| `ATCSCC-GOLD-017` | `2026-05-19:079` | `GroundDelayProgramTMI` | 35 | `reviewed` |
| `ATCSCC-GOLD-018` | `2026-05-19:074` | `GroundDelayProgramTMI` | 62 | `reviewed` |
| `ATCSCC-GOLD-019` | `2026-05-15:067` | `GroundDelayProgramTMI` | 39 | `reviewed` |
| `ATCSCC-GOLD-020` | `2026-05-15:084` | `GroundDelayProgramTMI` | 34 | `reviewed` |
| `ATCSCC-GOLD-021` | `2026-05-14:089` | `GroundStopTMI` | 34 | `reviewed` |
| `ATCSCC-GOLD-022` | `2026-05-15:064` | `GroundDelayProgramTMI` | 43 | `reviewed` |
| `ATCSCC-GOLD-023` | `2026-05-20:163` | `GroundStopTMI` | 41 | `reviewed` |
| `ATCSCC-GOLD-024` | `2026-05-18:136` | `GroundStopTMI` | 46 | `reviewed` |
| `ATCSCC-GOLD-025` | `2026-05-18:144` | `GroundStopTMI` | 31 | `reviewed` |
| `ATCSCC-GOLD-026` | `2026-05-18:055` | `GroundStopTMI` | 40 | `reviewed` |
| `ATCSCC-GOLD-027` | `2026-05-19:110` | `GroundStopTMI` | 42 | `reviewed` |
| `ATCSCC-GOLD-028` | `2026-05-18:123` | `GroundStopTMI` | 36 | `reviewed` |
| `ATCSCC-GOLD-029` | `2026-05-18:001` | `GroundStopTMI` | 31 | `reviewed` |
| `ATCSCC-GOLD-030` | `2026-05-16:027` | `GroundStopTMI` | 39 | `reviewed` |
| `ATCSCC-GOLD-031` | `2026-05-19:011` | `GroundStopTMI` | 33 | `reviewed` |
| `ATCSCC-GOLD-032` | `2026-05-20:131` | `GroundStopTMI` | 38 | `reviewed` |
| `ATCSCC-GOLD-033` | `2026-05-18:025` | `GroundDelayProgramTMI` | 19 | `reviewed` |
| `ATCSCC-GOLD-034` | `2026-05-14:055` | `GroundDelayProgramTMI` | 24 | `reviewed` |
| `ATCSCC-GOLD-035` | `2026-05-20:084` | `GroundDelayProgramTMI` | 63 | `reviewed` |
| `ATCSCC-GOLD-036` | `2026-05-17:022` | `GroundDelayProgramTMI` | 47 | `reviewed` |
| `ATCSCC-GOLD-037` | `2026-05-14:040` | `GroundDelayProgramTMI` | 47 | `reviewed` |
| `ATCSCC-GOLD-038` | `2026-05-20:115` | `GroundDelayProgramTMI` | 31 | `reviewed` |
| `ATCSCC-GOLD-039` | `2026-05-18:075` | `GroundStopTMI` | 50 | `reviewed` |
| `ATCSCC-GOLD-040` | `2026-05-20:197` | `ReRouteTMI` | 15 | `reviewed` |
| `ATCSCC-GOLD-041` | `2026-05-18:054` | `ReRouteTMI` | 27 | `reviewed` |
| `ATCSCC-GOLD-042` | `2026-05-20:015` | `ReRouteTMI` | 25 | `reviewed` |
| `ATCSCC-GOLD-043` | `2026-05-19:008` | `ReRouteTMI` | 19 | `reviewed` |
| `ATCSCC-GOLD-044` | `2026-05-16:026` | `ReRouteTMI` | 43 | `reviewed` |
| `ATCSCC-GOLD-045` | `2026-05-20:150` | `ReRouteTMI` | 28 | `reviewed` |
| `ATCSCC-GOLD-046` | `2026-05-18:040` | `TrafficManagementInitiative` | 17 | `reviewed` |
| `ATCSCC-GOLD-047` | `2026-05-14:033` | `TrafficManagementInitiative` | 19 | `reviewed` |
| `ATCSCC-GOLD-048` | `2026-05-17:003` | `TrafficManagementInitiative` | 16 | `reviewed` |
| `ATCSCC-GOLD-049` | `2026-05-19:013` | `TrafficManagementInitiative` | 20 | `reviewed` |
| `ATCSCC-GOLD-050` | `2026-05-19:043` | `TrafficManagementInitiative` | 29 | `reviewed` |
| `ATCSCC-GOLD-051` | `2026-05-14:030` | `TrafficManagementInitiative` | 25 | `reviewed` |
| `ATCSCC-GOLD-052` | `2026-05-20:119` | `GroundStopTMI` | 44 | `reviewed` |
| `ATCSCC-GOLD-053` | `2026-05-18:125` | `GroundStopTMI` | 32 | `reviewed` |
| `ATCSCC-GOLD-054` | `2026-05-20:153` | `GroundStopTMI` | 43 | `reviewed` |
| `ATCSCC-GOLD-055` | `2026-05-20:179` | `GroundStopTMI` | 34 | `reviewed` |
| `ATCSCC-GOLD-056` | `2026-05-17:041` | `TrafficManagementInitiative` | 30 | `reviewed` |
| `ATCSCC-GOLD-057` | `2026-05-14:007` | `GroundStopTMI` | 44 | `reviewed` |
| `ATCSCC-GOLD-058` | `2026-05-20:139` | `GroundStopTMI` | 44 | `reviewed` |
| `ATCSCC-GOLD-059` | `2026-05-14:086` | `TrafficManagementInitiative` | 38 | `reviewed` |
| `ATCSCC-GOLD-060` | `2026-05-17:050` | `TrafficManagementInitiative` | 24 | `reviewed` |
| `ATCSCC-GOLD-061` | `2026-05-15:017` | `TrafficManagementInitiative` | 28 | `reviewed` |
| `ATCSCC-GOLD-062` | `2026-05-20:029` | `TrafficManagementInitiative` | 26 | `reviewed` |
| `ATCSCC-GOLD-063` | `2026-05-16:035` | `TrafficManagementInitiative` | 24 | `reviewed` |
| `ATCSCC-GOLD-064` | `2026-05-19:112` | `TrafficManagementInitiative` | 32 | `reviewed` |
| `ATCSCC-GOLD-065` | `2026-05-16:061` | `TrafficManagementInitiative` | 40 | `reviewed` |
| `ATCSCC-GOLD-066` | `2026-05-17:011` | `TrafficManagementInitiative` | 20 | `reviewed` |
| `ATCSCC-GOLD-067` | `2026-05-15:030` | `TrafficManagementInitiative` | 27 | `reviewed` |
| `ATCSCC-GOLD-068` | `2026-05-18:126` | `TrafficManagementInitiative` | 27 | `reviewed` |
| `ATCSCC-GOLD-069` | `2026-05-20:192` | `TrafficManagementInitiative` | 20 | `reviewed` |
| `ATCSCC-GOLD-070` | `2026-05-14:014` | `TrafficManagementInitiative` | 19 | `reviewed` |
| `ATCSCC-GOLD-071` | `2026-05-19:064` | `TrafficManagementInitiative` | 25 | `reviewed` |
| `ATCSCC-GOLD-072` | `2026-05-17:065` | `TrafficManagementInitiative` | 28 | `reviewed` |
| `ATCSCC-GOLD-073` | `2026-05-20:006` | `GroundStopTMI` | 32 | `reviewed` |
| `ATCSCC-GOLD-074` | `2026-05-14:073` | `TrafficManagementInitiative` | 32 | `reviewed` |
| `ATCSCC-GOLD-075` | `2026-05-18:119` | `TrafficManagementInitiative` | 21 | `reviewed` |
| `ATCSCC-GOLD-076` | `2026-05-20:013` | `TrafficManagementInitiative` | 23 | `reviewed` |
| `ATCSCC-GOLD-077` | `2026-05-19:001` | `TrafficManagementInitiative` | 29 | `reviewed` |
| `ATCSCC-GOLD-078` | `2026-05-20:026` | `TrafficManagementInitiative` | 22 | `reviewed` |
| `ATCSCC-GOLD-079` | `2026-05-15:051` | `ReRouteTMI` | 24 | `reviewed` |
| `ATCSCC-GOLD-080` | `2026-05-18:148` | `TrafficManagementInitiative` | 19 | `reviewed` |
| `ATCSCC-GOLD-081` | `2026-05-18:023` | `GroundDelayProgramTMI` | 37 | `reviewed` |
| `ATCSCC-GOLD-082` | `2026-05-20:145` | `ReRouteTMI` | 51 | `reviewed` |
| `ATCSCC-GOLD-083` | `2026-05-20:016` | `GroundStopTMI` | 23 | `reviewed` |
| `ATCSCC-GOLD-084` | `2026-05-17:017` | `ReRouteTMI` | 31 | `reviewed` |
| `ATCSCC-GOLD-085` | `2026-05-19:009` | `TrafficManagementInitiative` | 17 | `reviewed` |
| `ATCSCC-GOLD-086` | `2026-05-16:046` | `TrafficManagementInitiative` | 26 | `reviewed` |
| `ATCSCC-GOLD-087` | `2026-05-18:107` | `TrafficManagementInitiative` | 24 | `reviewed` |
| `ATCSCC-GOLD-088` | `2026-05-18:021` | `GroundDelayProgramTMI` | 26 | `reviewed` |
| `ATCSCC-GOLD-089` | `2026-05-16:018` | `ReRouteTMI` | 25 | `reviewed` |
| `ATCSCC-GOLD-090` | `2026-05-15:061` | `ReRouteTMI` | 19 | `reviewed` |
| `ATCSCC-GOLD-091` | `2026-05-19:068` | `GroundStopTMI` | 33 | `reviewed` |
| `ATCSCC-GOLD-092` | `2026-05-15:075` | `GroundDelayProgramTMI` | 45 | `reviewed` |
| `ATCSCC-GOLD-093` | `2026-05-18:060` | `GroundDelayProgramTMI` | 27 | `reviewed` |
| `ATCSCC-GOLD-094` | `2026-05-20:068` | `TrafficManagementInitiative` | 20 | `reviewed` |
| `ATCSCC-GOLD-095` | `2026-05-19:047` | `ReRouteTMI` | 17 | `reviewed` |
| `ATCSCC-GOLD-096` | `2026-05-15:087` | `TrafficManagementInitiative` | 25 | `reviewed` |
| `ATCSCC-GOLD-097` | `2026-05-16:067` | `ReRouteTMI` | 13 | `reviewed` |
| `ATCSCC-GOLD-098` | `2026-05-20:100` | `ReRouteTMI` | 55 | `reviewed` |
| `ATCSCC-GOLD-099` | `2026-05-20:004` | `TrafficManagementInitiative` | 19 | `reviewed` |
| `ATCSCC-GOLD-100` | `2026-05-17:071` | `TrafficManagementInitiative` | 30 | `reviewed` |

## High-Load Samples

| Sample | Source | Candidate clusters | Dominant systems |
| --- | --- | ---: | --- |
| `ATCSCC-GOLD-035` | `2026-05-20:084` | 63 | `{"S0_rule_only": 8, "S1_llm_only": 18, "S1b_llm_canonicalized": 30, "S2_llm_schema_slice": 3, "S3_llm_schema_slice_validator_repair": 6, "S4_hybrid_backbone_enrichment": 11}` |
| `ATCSCC-GOLD-018` | `2026-05-19:074` | 62 | `{"S0_rule_only": 8, "S1_llm_only": 19, "S1b_llm_canonicalized": 23, "S2_llm_schema_slice": 6, "S3_llm_schema_slice_validator_repair": 7, "S4_hybrid_backbone_enrichment": 7}` |
| `ATCSCC-GOLD-098` | `2026-05-20:100` | 55 | `{"S0_rule_only": 5, "S1_llm_only": 16, "S1b_llm_canonicalized": 8, "S2_llm_schema_slice": 12, "S3_llm_schema_slice_validator_repair": 16, "S4_hybrid_backbone_enrichment": 10}` |
| `ATCSCC-GOLD-082` | `2026-05-20:145` | 51 | `{"S0_rule_only": 5, "S1_llm_only": 17, "S1b_llm_canonicalized": 8, "S2_llm_schema_slice": 11, "S3_llm_schema_slice_validator_repair": 11, "S4_hybrid_backbone_enrichment": 9}` |
| `ATCSCC-GOLD-039` | `2026-05-18:075` | 50 | `{"S0_rule_only": 1, "S1_llm_only": 18, "S1b_llm_canonicalized": 2, "S2_llm_schema_slice": 21, "S3_llm_schema_slice_validator_repair": 8, "S4_hybrid_backbone_enrichment": 9}` |
| `ATCSCC-GOLD-036` | `2026-05-17:022` | 47 | `{"S0_rule_only": 8, "S1_llm_only": 17, "S1b_llm_canonicalized": 7, "S2_llm_schema_slice": 8, "S3_llm_schema_slice_validator_repair": 8, "S4_hybrid_backbone_enrichment": 8}` |
| `ATCSCC-GOLD-037` | `2026-05-14:040` | 47 | `{"S0_rule_only": 8, "S1_llm_only": 19, "S1b_llm_canonicalized": 3, "S2_llm_schema_slice": 9, "S3_llm_schema_slice_validator_repair": 9, "S4_hybrid_backbone_enrichment": 12}` |
| `ATCSCC-GOLD-010` | `2026-05-20:053` | 46 | `{"S0_rule_only": 5, "S1_llm_only": 12, "S1b_llm_canonicalized": 9, "S2_llm_schema_slice": 13, "S3_llm_schema_slice_validator_repair": 9, "S4_hybrid_backbone_enrichment": 4}` |
| `ATCSCC-GOLD-014` | `2026-05-18:104` | 46 | `{"S0_rule_only": 5, "S1_llm_only": 14, "S1b_llm_canonicalized": 8, "S2_llm_schema_slice": 11, "S3_llm_schema_slice_validator_repair": 9, "S4_hybrid_backbone_enrichment": 4}` |
| `ATCSCC-GOLD-024` | `2026-05-18:136` | 46 | `{"S0_rule_only": 9, "S1_llm_only": 19, "S1b_llm_canonicalized": 14, "S2_llm_schema_slice": 6, "S4_hybrid_backbone_enrichment": 7}` |
| `ATCSCC-GOLD-011` | `2026-05-19:108` | 45 | `{"S0_rule_only": 5, "S1_llm_only": 17, "S1b_llm_canonicalized": 4, "S2_llm_schema_slice": 10, "S3_llm_schema_slice_validator_repair": 11, "S4_hybrid_backbone_enrichment": 9}` |
| `ATCSCC-GOLD-092` | `2026-05-15:075` | 45 | `{"S0_rule_only": 9, "S1_llm_only": 12, "S1b_llm_canonicalized": 13, "S2_llm_schema_slice": 8, "S3_llm_schema_slice_validator_repair": 5, "S4_hybrid_backbone_enrichment": 13}` |
| `ATCSCC-GOLD-052` | `2026-05-20:119` | 44 | `{"S0_rule_only": 9, "S1_llm_only": 17, "S1b_llm_canonicalized": 12, "S2_llm_schema_slice": 7, "S3_llm_schema_slice_validator_repair": 5, "S4_hybrid_backbone_enrichment": 11}` |
| `ATCSCC-GOLD-057` | `2026-05-14:007` | 44 | `{"S0_rule_only": 9, "S1_llm_only": 9, "S1b_llm_canonicalized": 8, "S2_llm_schema_slice": 16, "S3_llm_schema_slice_validator_repair": 3, "S4_hybrid_backbone_enrichment": 11}` |
| `ATCSCC-GOLD-058` | `2026-05-20:139` | 44 | `{"S0_rule_only": 9, "S1_llm_only": 15, "S1b_llm_canonicalized": 19, "S2_llm_schema_slice": 7, "S3_llm_schema_slice_validator_repair": 1, "S4_hybrid_backbone_enrichment": 8}` |
| `ATCSCC-GOLD-022` | `2026-05-15:064` | 43 | `{"S0_rule_only": 8, "S1_llm_only": 18, "S1b_llm_canonicalized": 3, "S2_llm_schema_slice": 13, "S3_llm_schema_slice_validator_repair": 4, "S4_hybrid_backbone_enrichment": 9}` |
| `ATCSCC-GOLD-044` | `2026-05-16:026` | 43 | `{"S0_rule_only": 2, "S1_llm_only": 16, "S1b_llm_canonicalized": 3, "S2_llm_schema_slice": 13, "S3_llm_schema_slice_validator_repair": 9, "S4_hybrid_backbone_enrichment": 2}` |
| `ATCSCC-GOLD-054` | `2026-05-20:153` | 43 | `{"S0_rule_only": 9, "S1_llm_only": 10, "S1b_llm_canonicalized": 11, "S2_llm_schema_slice": 8, "S3_llm_schema_slice_validator_repair": 8, "S4_hybrid_backbone_enrichment": 8}` |
| `ATCSCC-GOLD-027` | `2026-05-19:110` | 42 | `{"S0_rule_only": 9, "S1_llm_only": 12, "S1b_llm_canonicalized": 10, "S2_llm_schema_slice": 7, "S3_llm_schema_slice_validator_repair": 6, "S4_hybrid_backbone_enrichment": 9}` |
| `ATCSCC-GOLD-012` | `2026-05-18:053` | 41 | `{"S0_rule_only": 5, "S1_llm_only": 12, "S1b_llm_canonicalized": 7, "S2_llm_schema_slice": 9, "S3_llm_schema_slice_validator_repair": 9, "S4_hybrid_backbone_enrichment": 9}` |
