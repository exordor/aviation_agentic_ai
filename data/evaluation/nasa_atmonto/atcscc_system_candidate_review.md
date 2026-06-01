# NASA ATMONTO Cross-System Candidate Review

- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Candidate review JSONL: `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.jsonl`
- Records: 100
- Candidate clusters: 2272
- Raw fact counts by system: `{"S0_rule_only": 615, "S1_llm_only": 1211, "S2_llm_schema_slice": 326, "S3_llm_schema_slice_validator_repair": 137}`
- Cluster counts by system: `{"S0_rule_only": 609, "S1_llm_only": 1209, "S2_llm_schema_slice": 322, "S3_llm_schema_slice_validator_repair": 137}`
- Candidate kinds: `{"canonical_fact": 609, "freeform_or_unmapped_fact": 1522, "property_bundle": 113, "schema_shaped_object": 28}`

## Completion Gate

- Use this cross-system candidate package during manual gold review so S1-S3 facts are considered alongside the rule-only baseline. It is not itself reviewed gold and must not be scored as manual truth.

## Review Queue

| Sample | Source | Class | Candidate clusters | Status |
| --- | --- | --- | ---: | --- |
| `ATCSCC-GOLD-001` | `2026-05-19:032` | `ReRouteTMI` | 26 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-002` | `2026-05-15:063` | `TrafficManagementInitiative` | 20 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-003` | `2026-05-18:069` | `TrafficManagementInitiative` | 19 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-004` | `2026-05-14:059` | `TrafficManagementInitiative` | 22 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-005` | `2026-05-19:059` | `TrafficManagementInitiative` | 23 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-006` | `2026-05-19:144` | `GroundDelayProgramTMI` | 17 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-007` | `2026-05-16:051` | `TrafficManagementInitiative` | 14 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-008` | `2026-05-17:019` | `TrafficManagementInitiative` | 19 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-009` | `2026-05-20:040` | `ReRouteTMI` | 21 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-010` | `2026-05-20:053` | `ReRouteTMI` | 20 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-011` | `2026-05-19:108` | `ReRouteTMI` | 33 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-012` | `2026-05-18:053` | `ReRouteTMI` | 27 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-013` | `2026-05-18:124` | `ReRouteTMI` | 31 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-014` | `2026-05-18:104` | `ReRouteTMI` | 31 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-015` | `2026-05-20:137` | `ReRouteTMI` | 22 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-016` | `2026-05-20:078` | `ReRouteTMI` | 29 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-017` | `2026-05-19:079` | `GroundDelayProgramTMI` | 25 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-018` | `2026-05-19:074` | `GroundDelayProgramTMI` | 29 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-019` | `2026-05-15:067` | `GroundDelayProgramTMI` | 33 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-020` | `2026-05-15:084` | `GroundDelayProgramTMI` | 26 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-021` | `2026-05-14:089` | `GroundStopTMI` | 21 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-022` | `2026-05-15:064` | `GroundDelayProgramTMI` | 40 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-023` | `2026-05-20:163` | `GroundStopTMI` | 30 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-024` | `2026-05-18:136` | `GroundStopTMI` | 34 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-025` | `2026-05-18:144` | `GroundStopTMI` | 29 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-026` | `2026-05-18:055` | `GroundStopTMI` | 31 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-027` | `2026-05-19:110` | `GroundStopTMI` | 23 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-028` | `2026-05-18:123` | `GroundStopTMI` | 33 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-029` | `2026-05-18:001` | `GroundStopTMI` | 23 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-030` | `2026-05-16:027` | `GroundStopTMI` | 33 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-031` | `2026-05-19:011` | `GroundStopTMI` | 23 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-032` | `2026-05-20:131` | `GroundStopTMI` | 30 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-033` | `2026-05-18:025` | `GroundDelayProgramTMI` | 19 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-034` | `2026-05-14:055` | `GroundDelayProgramTMI` | 19 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-035` | `2026-05-20:084` | `GroundDelayProgramTMI` | 28 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-036` | `2026-05-17:022` | `GroundDelayProgramTMI` | 34 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-037` | `2026-05-14:040` | `GroundDelayProgramTMI` | 29 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-038` | `2026-05-20:115` | `GroundDelayProgramTMI` | 25 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-039` | `2026-05-18:075` | `GroundStopTMI` | 27 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-040` | `2026-05-20:197` | `ReRouteTMI` | 15 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-041` | `2026-05-18:054` | `ReRouteTMI` | 18 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-042` | `2026-05-20:015` | `ReRouteTMI` | 15 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-043` | `2026-05-19:008` | `ReRouteTMI` | 10 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-044` | `2026-05-16:026` | `ReRouteTMI` | 24 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-045` | `2026-05-20:150` | `ReRouteTMI` | 23 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-046` | `2026-05-18:040` | `TrafficManagementInitiative` | 15 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-047` | `2026-05-14:033` | `TrafficManagementInitiative` | 18 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-048` | `2026-05-17:003` | `TrafficManagementInitiative` | 12 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-049` | `2026-05-19:013` | `TrafficManagementInitiative` | 20 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-050` | `2026-05-19:043` | `TrafficManagementInitiative` | 28 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-051` | `2026-05-14:030` | `TrafficManagementInitiative` | 22 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-052` | `2026-05-20:119` | `GroundStopTMI` | 28 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-053` | `2026-05-18:125` | `GroundStopTMI` | 25 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-054` | `2026-05-20:153` | `GroundStopTMI` | 28 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-055` | `2026-05-20:179` | `GroundStopTMI` | 28 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-056` | `2026-05-17:041` | `TrafficManagementInitiative` | 17 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-057` | `2026-05-14:007` | `GroundStopTMI` | 35 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-058` | `2026-05-20:139` | `GroundStopTMI` | 26 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-059` | `2026-05-14:086` | `TrafficManagementInitiative` | 22 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-060` | `2026-05-17:050` | `TrafficManagementInitiative` | 16 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-061` | `2026-05-15:017` | `TrafficManagementInitiative` | 26 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-062` | `2026-05-20:029` | `TrafficManagementInitiative` | 25 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-063` | `2026-05-16:035` | `TrafficManagementInitiative` | 16 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-064` | `2026-05-19:112` | `TrafficManagementInitiative` | 16 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-065` | `2026-05-16:061` | `TrafficManagementInitiative` | 33 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-066` | `2026-05-17:011` | `TrafficManagementInitiative` | 17 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-067` | `2026-05-15:030` | `TrafficManagementInitiative` | 26 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-068` | `2026-05-18:126` | `TrafficManagementInitiative` | 17 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-069` | `2026-05-20:192` | `TrafficManagementInitiative` | 16 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-070` | `2026-05-14:014` | `TrafficManagementInitiative` | 18 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-071` | `2026-05-19:064` | `TrafficManagementInitiative` | 13 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-072` | `2026-05-17:065` | `TrafficManagementInitiative` | 17 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-073` | `2026-05-20:006` | `GroundStopTMI` | 19 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-074` | `2026-05-14:073` | `TrafficManagementInitiative` | 29 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-075` | `2026-05-18:119` | `TrafficManagementInitiative` | 20 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-076` | `2026-05-20:013` | `TrafficManagementInitiative` | 15 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-077` | `2026-05-19:001` | `TrafficManagementInitiative` | 28 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-078` | `2026-05-20:026` | `TrafficManagementInitiative` | 22 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-079` | `2026-05-15:051` | `ReRouteTMI` | 16 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-080` | `2026-05-18:148` | `TrafficManagementInitiative` | 19 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-081` | `2026-05-18:023` | `GroundDelayProgramTMI` | 28 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-082` | `2026-05-20:145` | `ReRouteTMI` | 25 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-083` | `2026-05-20:016` | `GroundStopTMI` | 17 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-084` | `2026-05-17:017` | `ReRouteTMI` | 30 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-085` | `2026-05-19:009` | `TrafficManagementInitiative` | 15 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-086` | `2026-05-16:046` | `TrafficManagementInitiative` | 25 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-087` | `2026-05-18:107` | `TrafficManagementInitiative` | 18 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-088` | `2026-05-18:021` | `GroundDelayProgramTMI` | 18 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-089` | `2026-05-16:018` | `ReRouteTMI` | 18 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-090` | `2026-05-15:061` | `ReRouteTMI` | 10 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-091` | `2026-05-19:068` | `GroundStopTMI` | 24 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-092` | `2026-05-15:075` | `GroundDelayProgramTMI` | 23 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-093` | `2026-05-18:060` | `GroundDelayProgramTMI` | 19 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-094` | `2026-05-20:068` | `TrafficManagementInitiative` | 20 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-095` | `2026-05-19:047` | `ReRouteTMI` | 17 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-096` | `2026-05-15:087` | `TrafficManagementInitiative` | 24 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-097` | `2026-05-16:067` | `ReRouteTMI` | 10 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-098` | `2026-05-20:100` | `ReRouteTMI` | 23 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-099` | `2026-05-20:004` | `TrafficManagementInitiative` | 12 | `pending_manual_gold_annotation` |
| `ATCSCC-GOLD-100` | `2026-05-17:071` | `TrafficManagementInitiative` | 25 | `pending_manual_gold_annotation` |

## High-Load Samples

| Sample | Source | Candidate clusters | Dominant systems |
| --- | --- | ---: | --- |
| `ATCSCC-GOLD-022` | `2026-05-15:064` | 40 | `{"S0_rule_only": 8, "S1_llm_only": 18, "S2_llm_schema_slice": 13, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-057` | `2026-05-14:007` | 35 | `{"S0_rule_only": 9, "S1_llm_only": 9, "S2_llm_schema_slice": 16, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-024` | `2026-05-18:136` | 34 | `{"S0_rule_only": 9, "S1_llm_only": 19, "S2_llm_schema_slice": 6}` |
| `ATCSCC-GOLD-036` | `2026-05-17:022` | 34 | `{"S0_rule_only": 8, "S1_llm_only": 17, "S2_llm_schema_slice": 8, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-011` | `2026-05-19:108` | 33 | `{"S0_rule_only": 5, "S1_llm_only": 17, "S2_llm_schema_slice": 10, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-019` | `2026-05-15:067` | 33 | `{"S0_rule_only": 8, "S1_llm_only": 15, "S2_llm_schema_slice": 9, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-028` | `2026-05-18:123` | 33 | `{"S0_rule_only": 9, "S1_llm_only": 15, "S2_llm_schema_slice": 8, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-030` | `2026-05-16:027` | 33 | `{"S0_rule_only": 9, "S1_llm_only": 15, "S2_llm_schema_slice": 8, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-065` | `2026-05-16:061` | 33 | `{"S0_rule_only": 4, "S1_llm_only": 12, "S2_llm_schema_slice": 16, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-013` | `2026-05-18:124` | 31 | `{"S0_rule_only": 5, "S1_llm_only": 16, "S3_llm_schema_slice_validator_repair": 10}` |
| `ATCSCC-GOLD-014` | `2026-05-18:104` | 31 | `{"S0_rule_only": 5, "S1_llm_only": 14, "S2_llm_schema_slice": 11, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-026` | `2026-05-18:055` | 31 | `{"S0_rule_only": 9, "S1_llm_only": 12, "S2_llm_schema_slice": 6, "S3_llm_schema_slice_validator_repair": 7}` |
| `ATCSCC-GOLD-023` | `2026-05-20:163` | 30 | `{"S0_rule_only": 9, "S1_llm_only": 10, "S2_llm_schema_slice": 10, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-032` | `2026-05-20:131` | 30 | `{"S0_rule_only": 9, "S1_llm_only": 11, "S2_llm_schema_slice": 9, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-084` | `2026-05-17:017` | 30 | `{"S0_rule_only": 5, "S1_llm_only": 18, "S2_llm_schema_slice": 7}` |
| `ATCSCC-GOLD-016` | `2026-05-20:078` | 29 | `{"S0_rule_only": 5, "S1_llm_only": 15, "S2_llm_schema_slice": 8, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-018` | `2026-05-19:074` | 29 | `{"S0_rule_only": 8, "S1_llm_only": 19, "S2_llm_schema_slice": 1, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-025` | `2026-05-18:144` | 29 | `{"S0_rule_only": 9, "S1_llm_only": 12, "S2_llm_schema_slice": 8}` |
| `ATCSCC-GOLD-037` | `2026-05-14:040` | 29 | `{"S0_rule_only": 8, "S1_llm_only": 19, "S2_llm_schema_slice": 1, "S3_llm_schema_slice_validator_repair": 1}` |
| `ATCSCC-GOLD-074` | `2026-05-14:073` | 29 | `{"S0_rule_only": 4, "S1_llm_only": 24, "S2_llm_schema_slice": 1}` |
