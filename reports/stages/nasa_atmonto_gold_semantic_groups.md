# NASA ATMONTO Gold Semantic Groups

## Material Passport

- Artifact: semantic grouping report for the 100-record ATCSCC gold-set candidate.
- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Workload plan: `reports/stages/nasa_atmonto_gold_review_workload_plan.md`
- Classification method: deterministic ATCSCC advisory headline heuristics.
- Boundary: grouping is for stratified analysis; it is not an annotation decision and not a train/dev/test split.

## Summary

- Records: 100
- Semantic groups: 9
- Minimum group size: 1
- Candidate class counts: `{"GroundDelayProgramTMI": 16, "GroundStopTMI": 21, "ReRouteTMI": 23, "TrafficManagementInitiative": 40}`
- Source-date counts: `{"2026-05-14": 10, "2026-05-15": 10, "2026-05-16": 8, "2026-05-17": 9, "2026-05-18": 21, "2026-05-19": 17, "2026-05-20": 25}`

## Semantic Groups

| Group | Label | Records | Candidate classes | Priority lanes | Example samples |
| --- | --- | ---: | --- | --- | --- |
| `ground_stop_lifecycle` | Ground stop lifecycle | 26 | `{"GroundDelayProgramTMI": 1, "GroundStopTMI": 20, "TrafficManagementInitiative": 5}` | `{"1_rejection_adjudication": 17, "2_high_cross_system_coverage": 2, "3_standard_review": 7}` | `ATCSCC-GOLD-021, ATCSCC-GOLD-023, ATCSCC-GOLD-024, ATCSCC-GOLD-025, ATCSCC-GOLD-026, ATCSCC-GOLD-027, ATCSCC-GOLD-028, ATCSCC-GOLD-029` |
| `reroute_or_route_constraint` | Reroute or route constraint | 25 | `{"GroundStopTMI": 1, "ReRouteTMI": 20, "TrafficManagementInitiative": 4}` | `{"1_rejection_adjudication": 12, "2_high_cross_system_coverage": 4, "3_standard_review": 9}` | `ATCSCC-GOLD-001, ATCSCC-GOLD-005, ATCSCC-GOLD-007, ATCSCC-GOLD-009, ATCSCC-GOLD-010, ATCSCC-GOLD-011, ATCSCC-GOLD-012, ATCSCC-GOLD-013` |
| `volcanic_activity_bulletin` | Volcanic activity bulletin | 19 | `{"TrafficManagementInitiative": 19}` | `{"3_standard_review": 19}` | `ATCSCC-GOLD-046, ATCSCC-GOLD-047, ATCSCC-GOLD-049, ATCSCC-GOLD-050, ATCSCC-GOLD-051, ATCSCC-GOLD-061, ATCSCC-GOLD-062, ATCSCC-GOLD-066` |
| `ground_delay_program_lifecycle` | Ground delay program lifecycle | 12 | `{"GroundDelayProgramTMI": 12}` | `{"2_high_cross_system_coverage": 9, "3_standard_review": 3}` | `ATCSCC-GOLD-017, ATCSCC-GOLD-018, ATCSCC-GOLD-019, ATCSCC-GOLD-020, ATCSCC-GOLD-022, ATCSCC-GOLD-033, ATCSCC-GOLD-035, ATCSCC-GOLD-036` |
| `airport_arrival_or_scheduling_delay` | Airport arrival or scheduling delay | 10 | `{"TrafficManagementInitiative": 10}` | `{"1_rejection_adjudication": 5, "3_standard_review": 5}` | `ATCSCC-GOLD-002, ATCSCC-GOLD-003, ATCSCC-GOLD-004, ATCSCC-GOLD-008, ATCSCC-GOLD-059, ATCSCC-GOLD-063, ATCSCC-GOLD-064, ATCSCC-GOLD-071` |
| `hotline_or_webpage_status` | Hotline or webpage status | 3 | `{"ReRouteTMI": 2, "TrafficManagementInitiative": 1}` | `{"3_standard_review": 3}` | `ATCSCC-GOLD-043, ATCSCC-GOLD-048, ATCSCC-GOLD-089` |
| `airport_diversion_recovery` | Airport diversion recovery | 2 | `{"GroundDelayProgramTMI": 2}` | `{"3_standard_review": 2}` | `ATCSCC-GOLD-034, ATCSCC-GOLD-093` |
| `special_or_flow_constraint_fyi` | Special mission or flow-constraint FYI | 2 | `{"ReRouteTMI": 1, "TrafficManagementInitiative": 1}` | `{"2_high_cross_system_coverage": 1, "3_standard_review": 1}` | `ATCSCC-GOLD-045, ATCSCC-GOLD-065` |
| `flight_plan_drop_time_status` | Flight plan drop time status | 1 | `{"GroundDelayProgramTMI": 1}` | `{"1_rejection_adjudication": 1}` | `ATCSCC-GOLD-006` |

## Records

| Sample | Source | Date | Batch | Candidate class | Semantic group | Headline |
| --- | --- | --- | --- | --- | --- | --- |
| `ATCSCC-GOLD-001` | `2026-05-19:032` | `2026-05-19` | `batch_01` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD |
| `ATCSCC-GOLD-002` | `2026-05-15:063` | `2026-05-15` | `batch_01` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS |
| `ATCSCC-GOLD-003` | `2026-05-18:069` | `2026-05-18` | `batch_01` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 069 LAS/ZLA 05/18/2026 LAS AIRPORT ARRIVAL DELAYS |
| `ATCSCC-GOLD-004` | `2026-05-14:059` | `2026-05-14` | `batch_01` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 059 PHLC/ZNY 05/14/2026 EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| `ATCSCC-GOLD-005` | `2026-05-19:059` | `2026-05-19` | `batch_01` | `TrafficManagementInitiative` | `reroute_or_route_constraint` | ATCSCC ADVZY 059 DCC 05/19/2026 IAH HOU CDRS_FYI |
| `ATCSCC-GOLD-006` | `2026-05-19:144` | `2026-05-19` | `batch_01` | `GroundDelayProgramTMI` | `flight_plan_drop_time_status` | ATCSCC ADVZY 144 ZBW 05/19/2026 EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| `ATCSCC-GOLD-007` | `2026-05-16:051` | `2026-05-16` | `batch_01` | `TrafficManagementInitiative` | `reroute_or_route_constraint` | ATCSCC ADVZY 051 DCC/ZDV 05/16/2026 DEN CDRS_FYI |
| `ATCSCC-GOLD-008` | `2026-05-17:019` | `2026-05-17` | `batch_01` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 019 ZMA/DCC 05/17/2026 SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| `ATCSCC-GOLD-009` | `2026-05-20:040` | `2026-05-20` | `batch_01` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 040 DCC 05/20/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-010` | `2026-05-20:053` | `2026-05-20` | `batch_01` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 053 DCC 05/20/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-011` | `2026-05-19:108` | `2026-05-19` | `batch_02` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 108 DCC 05/19/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-012` | `2026-05-18:053` | `2026-05-18` | `batch_02` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 053 DCC 05/18/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-013` | `2026-05-18:124` | `2026-05-18` | `batch_02` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 124 DCC 05/18/2026 ROUTE RQD |
| `ATCSCC-GOLD-014` | `2026-05-18:104` | `2026-05-18` | `batch_02` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 104 DCC 05/18/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-015` | `2026-05-20:137` | `2026-05-20` | `batch_02` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 137 DCC 05/20/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-016` | `2026-05-20:078` | `2026-05-20` | `batch_02` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 078 DCC 05/20/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-017` | `2026-05-19:079` | `2026-05-19` | `batch_02` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 079 BNA/ZME 05/19/2026 CDM GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-018` | `2026-05-19:074` | `2026-05-19` | `batch_02` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 074 BNA/ZME 05/19/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-019` | `2026-05-15:067` | `2026-05-15` | `batch_02` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 067 BNA/ZME 05/15/2026 CDM GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-020` | `2026-05-15:084` | `2026-05-15` | `batch_02` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 084 SFO/ZOA 05/15/2026 CDM GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-021` | `2026-05-14:089` | `2026-05-14` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 089 BNA/ZME 05/14/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-022` | `2026-05-15:064` | `2026-05-15` | `batch_03` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 064 BNA/ZME 05/15/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-023` | `2026-05-20:163` | `2026-05-20` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 163 DEN/ZDV 05/20/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-024` | `2026-05-18:136` | `2026-05-18` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 136 BNA/ZME 05/18/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-025` | `2026-05-18:144` | `2026-05-18` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 144 DTW/ZOB 05/18/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-026` | `2026-05-18:055` | `2026-05-18` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 055 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-027` | `2026-05-19:110` | `2026-05-19` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 110 ORD/ZAU 05/19/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-028` | `2026-05-18:123` | `2026-05-18` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 123 MSP/ZMP 05/18/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-029` | `2026-05-18:001` | `2026-05-18` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 001 DEN/ZDV 05/18/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-030` | `2026-05-16:027` | `2026-05-16` | `batch_03` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 027 ORD/ZAU 05/16/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-031` | `2026-05-19:011` | `2026-05-19` | `batch_04` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 011 SFO/ZOA 05/19/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-032` | `2026-05-20:131` | `2026-05-20` | `batch_04` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 131 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-033` | `2026-05-18:025` | `2026-05-18` | `batch_04` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 025 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `ATCSCC-GOLD-034` | `2026-05-14:055` | `2026-05-14` | `batch_04` | `GroundDelayProgramTMI` | `airport_diversion_recovery` | ATCSCC ADVZY 055 SAN/ZLA 05/14/2026 SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| `ATCSCC-GOLD-035` | `2026-05-20:084` | `2026-05-20` | `batch_04` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 084 EWR/ZNY 05/20/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-036` | `2026-05-17:022` | `2026-05-17` | `batch_04` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 022 SFO/ZOA 05/17/2026 CDM PROPOSED GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-037` | `2026-05-14:040` | `2026-05-14` | `batch_04` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 040 SFO/ZOA 05/14/2026 CDM GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-038` | `2026-05-20:115` | `2026-05-20` | `batch_04` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 115 LGA/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-039` | `2026-05-18:075` | `2026-05-18` | `batch_04` | `GroundStopTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 075 DCC/ZMA 05/18/2026 ZMA SWAP_FYI |
| `ATCSCC-GOLD-040` | `2026-05-20:197` | `2026-05-20` | `batch_04` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 197 DCC 05/20/2026 REROUTE CANCELLATION |
| `ATCSCC-GOLD-041` | `2026-05-18:054` | `2026-05-18` | `batch_05` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 054 DCC/ZNY 05/18/2026 OCEANIC ROUTE CLOSURE_RQD |
| `ATCSCC-GOLD-042` | `2026-05-20:015` | `2026-05-20` | `batch_05` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 015 DCC 05/20/2026 OCEANIC ROUTE CLOSURE_RQD |
| `ATCSCC-GOLD-043` | `2026-05-19:008` | `2026-05-19` | `batch_05` | `ReRouteTMI` | `hotline_or_webpage_status` | ATCSCC ADVZY 008 DCC 05/19/2026 EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| `ATCSCC-GOLD-044` | `2026-05-16:026` | `2026-05-16` | `batch_05` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 026 DCC/ZAU 05/16/2026 ZAU SWAP_FYI |
| `ATCSCC-GOLD-045` | `2026-05-20:150` | `2026-05-20` | `batch_05` | `ReRouteTMI` | `special_or_flow_constraint_fyi` | ATCSCC ADVZY 150 DCC/ZHU 05/20/2026 STARSHIP PRE-MISSION ADVISORY_FYI |
| `ATCSCC-GOLD-046` | `2026-05-18:040` | `2026-05-18` | `batch_05` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 040 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `ATCSCC-GOLD-047` | `2026-05-14:033` | `2026-05-14` | `batch_05` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 033 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `ATCSCC-GOLD-048` | `2026-05-17:003` | `2026-05-17` | `batch_05` | `TrafficManagementInitiative` | `hotline_or_webpage_status` | ATCSCC ADVZY 003 DCC 05/17/2026 TTCA/HOTLINE WEB PAGE TERMINATION |
| `ATCSCC-GOLD-049` | `2026-05-19:013` | `2026-05-19` | `batch_05` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 013 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `ATCSCC-GOLD-050` | `2026-05-19:043` | `2026-05-19` | `batch_05` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 043 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `ATCSCC-GOLD-051` | `2026-05-14:030` | `2026-05-14` | `batch_06` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 030 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - SANTA |
| `ATCSCC-GOLD-052` | `2026-05-20:119` | `2026-05-20` | `batch_06` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 119 IAD/ZDC 05/20/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-053` | `2026-05-18:125` | `2026-05-18` | `batch_06` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 125 STL/ZKC 05/18/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-054` | `2026-05-20:153` | `2026-05-20` | `batch_06` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 153 BWI/ZDC 05/20/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-055` | `2026-05-20:179` | `2026-05-20` | `batch_06` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 179 PHL/ZNY 05/20/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-056` | `2026-05-17:041` | `2026-05-17` | `batch_06` | `TrafficManagementInitiative` | `reroute_or_route_constraint` | ATCSCC ADVZY 041 DCC 05/17/2026 MIA FLL CDRS_FYI |
| `ATCSCC-GOLD-057` | `2026-05-14:007` | `2026-05-14` | `batch_06` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 007 DCA/ZDC 05/14/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-058` | `2026-05-20:139` | `2026-05-20` | `batch_06` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 139 DCA/ZDC 05/20/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-059` | `2026-05-14:086` | `2026-05-14` | `batch_06` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 086 MSP/ZMP 05/14/2026 MSP AIRPORT ARRIVAL DELAYS |
| `ATCSCC-GOLD-060` | `2026-05-17:050` | `2026-05-17` | `batch_06` | `TrafficManagementInitiative` | `ground_stop_lifecycle` | ATCSCC ADVZY 050 DCA/ZDC 05/17/2026 CDM GS CNX |
| `ATCSCC-GOLD-061` | `2026-05-15:017` | `2026-05-15` | `batch_07` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 017 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `ATCSCC-GOLD-062` | `2026-05-20:029` | `2026-05-20` | `batch_07` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 029 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `ATCSCC-GOLD-063` | `2026-05-16:035` | `2026-05-16` | `batch_07` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 035 ORD/ZAU 05/16/2026 ORD AIRPORT ARRIVAL DELAYS |
| `ATCSCC-GOLD-064` | `2026-05-19:112` | `2026-05-19` | `batch_07` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 112 DFW/ZFW 05/19/2026 DFW AIRPORT ARRIVAL DELAYS |
| `ATCSCC-GOLD-065` | `2026-05-16:061` | `2026-05-16` | `batch_07` | `TrafficManagementInitiative` | `special_or_flow_constraint_fyi` | ATCSCC ADVZY 061 DCC 05/16/2026 DEN CAPPING TUNNELING FYI |
| `ATCSCC-GOLD-066` | `2026-05-17:011` | `2026-05-17` | `batch_07` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 011 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `ATCSCC-GOLD-067` | `2026-05-15:030` | `2026-05-15` | `batch_07` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 030 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| `ATCSCC-GOLD-068` | `2026-05-18:126` | `2026-05-18` | `batch_07` | `TrafficManagementInitiative` | `ground_stop_lifecycle` | ATCSCC ADVZY 126 STL/ZKC 05/18/2026 CDM GS CNX |
| `ATCSCC-GOLD-069` | `2026-05-20:192` | `2026-05-20` | `batch_07` | `TrafficManagementInitiative` | `ground_stop_lifecycle` | ATCSCC ADVZY 192 PHL/ZNY 05/20/2026 CDM GS CNX |
| `ATCSCC-GOLD-070` | `2026-05-14:014` | `2026-05-14` | `batch_07` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 014 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `ATCSCC-GOLD-071` | `2026-05-19:064` | `2026-05-19` | `batch_08` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 064 EWR/ZNY 05/19/2026 EWR AIRPORT ARRIVAL DELAYS |
| `ATCSCC-GOLD-072` | `2026-05-17:065` | `2026-05-17` | `batch_08` | `TrafficManagementInitiative` | `reroute_or_route_constraint` | ATCSCC ADVZY 065 DCC/ZAU 05/17/2026 ORD MDW CDRS_FYI |
| `ATCSCC-GOLD-073` | `2026-05-20:006` | `2026-05-20` | `batch_08` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 006 DFW/ZFW 05/20/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-074` | `2026-05-14:073` | `2026-05-14` | `batch_08` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 073 DCC 05/14/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `ATCSCC-GOLD-075` | `2026-05-18:119` | `2026-05-18` | `batch_08` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 119 DCC 05/18/2026 VOLCANIC ACTIVITY BULLETIN - PURACE |
| `ATCSCC-GOLD-076` | `2026-05-20:013` | `2026-05-20` | `batch_08` | `TrafficManagementInitiative` | `ground_stop_lifecycle` | ATCSCC ADVZY 013 ORD/ZAU 05/20/2026 CDM GS CNX |
| `ATCSCC-GOLD-077` | `2026-05-19:001` | `2026-05-19` | `batch_08` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 001 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| `ATCSCC-GOLD-078` | `2026-05-20:026` | `2026-05-20` | `batch_08` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 026 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `ATCSCC-GOLD-079` | `2026-05-15:051` | `2026-05-15` | `batch_08` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 051 DCC/ZNY/ZMA 05/15/2026 OCEANIC ROUTE CLOSURES_RQD |
| `ATCSCC-GOLD-080` | `2026-05-18:148` | `2026-05-18` | `batch_08` | `TrafficManagementInitiative` | `ground_stop_lifecycle` | ATCSCC ADVZY 148 BNA/ZME 05/18/2026 CDM GS CNX |
| `ATCSCC-GOLD-081` | `2026-05-18:023` | `2026-05-18` | `batch_09` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 023 LAS/ZLA 05/18/2026 CDM GROUND DELAY PROGRAM |
| `ATCSCC-GOLD-082` | `2026-05-20:145` | `2026-05-20` | `batch_09` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 145 DCC 05/20/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-083` | `2026-05-20:016` | `2026-05-20` | `batch_09` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 016 LGA/JFK/ZNY 05/20/2026 LGA/JFK GROUND STOP CANCELLATION FOR DAL AND SUBS |
| `ATCSCC-GOLD-084` | `2026-05-17:017` | `2026-05-17` | `batch_09` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 017 DCC/ZNY 05/17/2026 ZNY SWAP_FYI |
| `ATCSCC-GOLD-085` | `2026-05-19:009` | `2026-05-19` | `batch_09` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 009 DCC 05/19/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| `ATCSCC-GOLD-086` | `2026-05-16:046` | `2026-05-16` | `batch_09` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 046 DCC 05/16/2026 VOLCANIC ACTIVITY BULLETIN - BEZYMIANNY |
| `ATCSCC-GOLD-087` | `2026-05-18:107` | `2026-05-18` | `batch_09` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 107 DEN/ZDV 05/18/2026 DEN AIRPORT SCHEDULING DELAYS |
| `ATCSCC-GOLD-088` | `2026-05-18:021` | `2026-05-18` | `batch_09` | `GroundDelayProgramTMI` | `ground_delay_program_lifecycle` | ATCSCC ADVZY 021 SFO/ZOA 05/18/2026 CDM GROUND DELAY PROGRAM CNX |
| `ATCSCC-GOLD-089` | `2026-05-16:018` | `2026-05-16` | `batch_09` | `ReRouteTMI` | `hotline_or_webpage_status` | ATCSCC ADVZY 018 DCC 05/16/2026 EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| `ATCSCC-GOLD-090` | `2026-05-15:061` | `2026-05-15` | `batch_09` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 061 DCC 05/15/2026 REROUTE CANCELLATION |
| `ATCSCC-GOLD-091` | `2026-05-19:068` | `2026-05-19` | `batch_10` | `GroundStopTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 068 IAH/ZHU 05/19/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-092` | `2026-05-15:075` | `2026-05-15` | `batch_10` | `GroundDelayProgramTMI` | `ground_stop_lifecycle` | ATCSCC ADVZY 075 BOS/ZBW 05/15/2026 CDM GROUND STOP |
| `ATCSCC-GOLD-093` | `2026-05-18:060` | `2026-05-18` | `batch_10` | `GroundDelayProgramTMI` | `airport_diversion_recovery` | ATCSCC ADVZY 060 STL/ZKC 05/18/2026 STL AIRPORT DIVERSION RECOVERY ACTIVATED |
| `ATCSCC-GOLD-094` | `2026-05-20:068` | `2026-05-20` | `batch_10` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 068 DCC 05/20/2026 VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| `ATCSCC-GOLD-095` | `2026-05-19:047` | `2026-05-19` | `batch_10` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 047 DCC 05/19/2026 REROUTE CANCELLATION |
| `ATCSCC-GOLD-096` | `2026-05-15:087` | `2026-05-15` | `batch_10` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 087 DCC 05/15/2026 VOLCANIC ACTIVITY BULLETIN - FUEGO |
| `ATCSCC-GOLD-097` | `2026-05-16:067` | `2026-05-16` | `batch_10` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 067 DCC 05/16/2026 REROUTE CANCELLATION |
| `ATCSCC-GOLD-098` | `2026-05-20:100` | `2026-05-20` | `batch_10` | `ReRouteTMI` | `reroute_or_route_constraint` | ATCSCC ADVZY 100 DCC 05/20/2026 ROUTE RQD /FL |
| `ATCSCC-GOLD-099` | `2026-05-20:004` | `2026-05-20` | `batch_10` | `TrafficManagementInitiative` | `airport_arrival_or_scheduling_delay` | ATCSCC ADVZY 004 MEM/ZME 05/20/2026 MEM AIRPORT ARRIVAL DELAYS |
| `ATCSCC-GOLD-100` | `2026-05-17:071` | `2026-05-17` | `batch_10` | `TrafficManagementInitiative` | `volcanic_activity_bulletin` | ATCSCC ADVZY 071 DCC 05/17/2026 VOLCANIC ACTIVITY BULLETIN - REVENTADOR |

## Use In Experiment

- Use these groups for stratified error analysis and per-group reporting. They are not train/dev/test splits and do not create gold truth by themselves.

## Limitations

- Grouping is based on deterministic headline heuristics, not domain-expert taxonomy.
- Small groups should be merged or reported descriptively if confidence intervals are unstable.
- Ontology candidate classes and operational semantic groups intentionally differ for status/cancellation/FYI notices.
