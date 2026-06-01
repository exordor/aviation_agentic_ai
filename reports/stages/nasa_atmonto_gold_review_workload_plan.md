# NASA ATMONTO Gold Review Workload Plan

- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Worklist: `data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.md`
- Candidate review: `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.jsonl`
- Batch index: `data/evaluation/nasa_atmonto/review_batches/index.md`
- Decision templates: `data/evaluation/nasa_atmonto/review_decisions/index.md`
- Progress tracker: `data/evaluation/nasa_atmonto/gold_review_progress.md`
- Records: 100
- Batches: 10
- Records with validator rejections: 40
- Rejected facts to adjudicate: 48
- Estimated total review time: 1965 minutes (32.75 hours)
- Complexity counts: `{"heavy": 45, "light": 13, "medium": 42}`
- Priority lanes: `{"1_rejection_adjudication": 40, "2_high_cross_system_coverage": 11, "3_standard_review": 49}`

## Priority Lanes

| Lane | Meaning |
| --- | --- |
| `1_rejection_adjudication` | Review first: these records need both semantic gold decisions and rejected-fact adjudications. |
| `2_high_cross_system_coverage` | Review next: no pilot rejection, but many cross-system candidate alternatives need source checks. |
| `3_standard_review` | Complete after the higher-workload lanes; still required for final recall/F1. |

## Batch Workload

| Batch | Samples | Records | Clusters | Cross-system clusters | Rejected facts | Est. min | Complexity | Lanes | File |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `batch_01` | `ATCSCC-GOLD-001`-`ATCSCC-GOLD-010` | 10 | 321 | 313 | 14 | 212 | `{"heavy": 6, "medium": 4}` | `{"1_rejection_adjudication": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_01.md` |
| `batch_02` | `ATCSCC-GOLD-011`-`ATCSCC-GOLD-020` | 10 | 416 | 411 | 10 | 253 | `{"heavy": 10}` | `{"1_rejection_adjudication": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_02.md` |
| `batch_03` | `ATCSCC-GOLD-021`-`ATCSCC-GOLD-030` | 10 | 383 | 370 | 13 | 240 | `{"heavy": 8, "medium": 2}` | `{"1_rejection_adjudication": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_03.md` |
| `batch_04` | `ATCSCC-GOLD-031`-`ATCSCC-GOLD-040` | 10 | 367 | 365 | 2 | 213 | `{"heavy": 6, "light": 2, "medium": 2}` | `{"1_rejection_adjudication": 2, "2_high_cross_system_coverage": 4, "3_standard_review": 4}` | `data/evaluation/nasa_atmonto/review_batches/batch_04.md` |
| `batch_05` | `ATCSCC-GOLD-041`-`ATCSCC-GOLD-050` | 10 | 243 | 243 | 0 | 155 | `{"heavy": 1, "light": 4, "medium": 5}` | `{"2_high_cross_system_coverage": 1, "3_standard_review": 9}` | `data/evaluation/nasa_atmonto/review_batches/batch_05.md` |
| `batch_06` | `ATCSCC-GOLD-051`-`ATCSCC-GOLD-060` | 10 | 358 | 350 | 9 | 221 | `{"heavy": 8, "medium": 2}` | `{"1_rejection_adjudication": 8, "3_standard_review": 2}` | `data/evaluation/nasa_atmonto/review_batches/batch_06.md` |
| `batch_07` | `ATCSCC-GOLD-061`-`ATCSCC-GOLD-070` | 10 | 263 | 263 | 0 | 163 | `{"heavy": 1, "light": 1, "medium": 8}` | `{"2_high_cross_system_coverage": 1, "3_standard_review": 9}` | `data/evaluation/nasa_atmonto/review_batches/batch_07.md` |
| `batch_08` | `ATCSCC-GOLD-071`-`ATCSCC-GOLD-080` | 10 | 255 | 255 | 0 | 160 | `{"light": 1, "medium": 9}` | `{"3_standard_review": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_08.md` |
| `batch_09` | `ATCSCC-GOLD-081`-`ATCSCC-GOLD-090` | 10 | 279 | 279 | 0 | 172 | `{"heavy": 2, "light": 2, "medium": 6}` | `{"2_high_cross_system_coverage": 2, "3_standard_review": 8}` | `data/evaluation/nasa_atmonto/review_batches/batch_09.md` |
| `batch_10` | `ATCSCC-GOLD-091`-`ATCSCC-GOLD-100` | 10 | 284 | 284 | 0 | 176 | `{"heavy": 3, "light": 3, "medium": 4}` | `{"2_high_cross_system_coverage": 3, "3_standard_review": 7}` | `data/evaluation/nasa_atmonto/review_batches/batch_10.md` |

## Recommended Review Order

| Order | Sample | Batch | Lane | Tier | Score | Est. min | Clusters | Cross-system | Rejected | Class |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `ATCSCC-GOLD-024` | `batch_03` | `1_rejection_adjudication` | `heavy` | 97 | 29 | 46 | 44 | 2 | `GroundStopTMI` |
| 2 | `ATCSCC-GOLD-023` | `batch_03` | `1_rejection_adjudication` | `heavy` | 87 | 27 | 41 | 39 | 2 | `GroundStopTMI` |
| 3 | `ATCSCC-GOLD-001` | `batch_01` | `1_rejection_adjudication` | `heavy` | 76 | 23 | 35 | 34 | 2 | `ReRouteTMI` |
| 4 | `ATCSCC-GOLD-021` | `batch_03` | `1_rejection_adjudication` | `heavy` | 73 | 24 | 34 | 32 | 2 | `GroundStopTMI` |
| 5 | `ATCSCC-GOLD-005` | `batch_01` | `1_rejection_adjudication` | `heavy` | 70 | 22 | 32 | 31 | 2 | `TrafficManagementInitiative` |
| 6 | `ATCSCC-GOLD-056` | `batch_06` | `1_rejection_adjudication` | `heavy` | 66 | 21 | 30 | 29 | 2 | `TrafficManagementInitiative` |
| 7 | `ATCSCC-GOLD-006` | `batch_01` | `1_rejection_adjudication` | `medium` | 54 | 19 | 24 | 23 | 2 | `GroundDelayProgramTMI` |
| 8 | `ATCSCC-GOLD-007` | `batch_01` | `1_rejection_adjudication` | `medium` | 54 | 18 | 24 | 23 | 2 | `TrafficManagementInitiative` |
| 9 | `ATCSCC-GOLD-018` | `batch_02` | `1_rejection_adjudication` | `heavy` | 127 | 34 | 62 | 61 | 1 | `GroundDelayProgramTMI` |
| 10 | `ATCSCC-GOLD-010` | `batch_01` | `1_rejection_adjudication` | `heavy` | 96 | 27 | 46 | 46 | 1 | `ReRouteTMI` |
| 11 | `ATCSCC-GOLD-014` | `batch_02` | `1_rejection_adjudication` | `heavy` | 96 | 27 | 46 | 46 | 1 | `ReRouteTMI` |
| 12 | `ATCSCC-GOLD-011` | `batch_02` | `1_rejection_adjudication` | `heavy` | 94 | 27 | 45 | 45 | 1 | `ReRouteTMI` |
| 13 | `ATCSCC-GOLD-052` | `batch_06` | `1_rejection_adjudication` | `heavy` | 91 | 26 | 44 | 43 | 1 | `GroundStopTMI` |
| 14 | `ATCSCC-GOLD-057` | `batch_06` | `1_rejection_adjudication` | `heavy` | 91 | 26 | 44 | 43 | 1 | `GroundStopTMI` |
| 15 | `ATCSCC-GOLD-058` | `batch_06` | `1_rejection_adjudication` | `heavy` | 91 | 26 | 44 | 43 | 1 | `GroundStopTMI` |
| 16 | `ATCSCC-GOLD-022` | `batch_03` | `1_rejection_adjudication` | `heavy` | 89 | 25 | 43 | 42 | 1 | `GroundDelayProgramTMI` |
| 17 | `ATCSCC-GOLD-054` | `batch_06` | `1_rejection_adjudication` | `heavy` | 89 | 25 | 43 | 42 | 1 | `GroundStopTMI` |
| 18 | `ATCSCC-GOLD-027` | `batch_03` | `1_rejection_adjudication` | `heavy` | 87 | 25 | 42 | 41 | 1 | `GroundStopTMI` |
| 19 | `ATCSCC-GOLD-012` | `batch_02` | `1_rejection_adjudication` | `heavy` | 86 | 25 | 41 | 41 | 1 | `ReRouteTMI` |
| 20 | `ATCSCC-GOLD-026` | `batch_03` | `1_rejection_adjudication` | `heavy` | 83 | 24 | 40 | 39 | 1 | `GroundStopTMI` |
| 21 | `ATCSCC-GOLD-013` | `batch_02` | `1_rejection_adjudication` | `heavy` | 82 | 24 | 39 | 39 | 1 | `ReRouteTMI` |
| 22 | `ATCSCC-GOLD-019` | `batch_02` | `1_rejection_adjudication` | `heavy` | 81 | 24 | 39 | 38 | 1 | `GroundDelayProgramTMI` |
| 23 | `ATCSCC-GOLD-030` | `batch_03` | `1_rejection_adjudication` | `heavy` | 81 | 24 | 39 | 38 | 1 | `GroundStopTMI` |
| 24 | `ATCSCC-GOLD-009` | `batch_01` | `1_rejection_adjudication` | `heavy` | 80 | 24 | 38 | 38 | 1 | `ReRouteTMI` |
| 25 | `ATCSCC-GOLD-016` | `batch_02` | `1_rejection_adjudication` | `heavy` | 79 | 24 | 38 | 37 | 1 | `ReRouteTMI` |
| 26 | `ATCSCC-GOLD-032` | `batch_04` | `1_rejection_adjudication` | `heavy` | 79 | 24 | 38 | 37 | 1 | `GroundStopTMI` |
| 27 | `ATCSCC-GOLD-059` | `batch_06` | `1_rejection_adjudication` | `heavy` | 79 | 23 | 38 | 37 | 1 | `TrafficManagementInitiative` |
| 28 | `ATCSCC-GOLD-015` | `batch_02` | `1_rejection_adjudication` | `heavy` | 78 | 24 | 37 | 37 | 1 | `ReRouteTMI` |
| 29 | `ATCSCC-GOLD-004` | `batch_01` | `1_rejection_adjudication` | `heavy` | 75 | 22 | 36 | 35 | 1 | `TrafficManagementInitiative` |
| 30 | `ATCSCC-GOLD-028` | `batch_03` | `1_rejection_adjudication` | `heavy` | 75 | 22 | 36 | 35 | 1 | `GroundStopTMI` |
| 31 | `ATCSCC-GOLD-017` | `batch_02` | `1_rejection_adjudication` | `heavy` | 73 | 22 | 35 | 34 | 1 | `GroundDelayProgramTMI` |
| 32 | `ATCSCC-GOLD-020` | `batch_02` | `1_rejection_adjudication` | `heavy` | 71 | 22 | 34 | 33 | 1 | `GroundDelayProgramTMI` |
| 33 | `ATCSCC-GOLD-055` | `batch_06` | `1_rejection_adjudication` | `heavy` | 71 | 22 | 34 | 33 | 1 | `GroundStopTMI` |
| 34 | `ATCSCC-GOLD-008` | `batch_01` | `1_rejection_adjudication` | `heavy` | 69 | 22 | 33 | 32 | 1 | `TrafficManagementInitiative` |
| 35 | `ATCSCC-GOLD-031` | `batch_04` | `1_rejection_adjudication` | `heavy` | 69 | 22 | 33 | 32 | 1 | `GroundStopTMI` |
| 36 | `ATCSCC-GOLD-053` | `batch_06` | `1_rejection_adjudication` | `heavy` | 67 | 21 | 32 | 31 | 1 | `GroundStopTMI` |
| 37 | `ATCSCC-GOLD-025` | `batch_03` | `1_rejection_adjudication` | `medium` | 65 | 20 | 31 | 30 | 1 | `GroundStopTMI` |
| 38 | `ATCSCC-GOLD-029` | `batch_03` | `1_rejection_adjudication` | `medium` | 65 | 20 | 31 | 30 | 1 | `GroundStopTMI` |
| 39 | `ATCSCC-GOLD-002` | `batch_01` | `1_rejection_adjudication` | `medium` | 61 | 19 | 29 | 28 | 1 | `TrafficManagementInitiative` |
| 40 | `ATCSCC-GOLD-003` | `batch_01` | `1_rejection_adjudication` | `medium` | 51 | 16 | 24 | 23 | 1 | `TrafficManagementInitiative` |
| 41 | `ATCSCC-GOLD-035` | `batch_04` | `2_high_cross_system_coverage` | `heavy` | 127 | 32 | 63 | 63 | 0 | `GroundDelayProgramTMI` |
| 42 | `ATCSCC-GOLD-098` | `batch_10` | `2_high_cross_system_coverage` | `heavy` | 111 | 29 | 55 | 55 | 0 | `ReRouteTMI` |
| 43 | `ATCSCC-GOLD-082` | `batch_09` | `2_high_cross_system_coverage` | `heavy` | 103 | 27 | 51 | 51 | 0 | `ReRouteTMI` |
| 44 | `ATCSCC-GOLD-039` | `batch_04` | `2_high_cross_system_coverage` | `heavy` | 101 | 27 | 50 | 50 | 0 | `GroundStopTMI` |
| 45 | `ATCSCC-GOLD-036` | `batch_04` | `2_high_cross_system_coverage` | `heavy` | 95 | 25 | 47 | 47 | 0 | `GroundDelayProgramTMI` |
| 46 | `ATCSCC-GOLD-037` | `batch_04` | `2_high_cross_system_coverage` | `heavy` | 95 | 25 | 47 | 47 | 0 | `GroundDelayProgramTMI` |
| 47 | `ATCSCC-GOLD-092` | `batch_10` | `2_high_cross_system_coverage` | `heavy` | 91 | 25 | 45 | 45 | 0 | `GroundDelayProgramTMI` |
| 48 | `ATCSCC-GOLD-044` | `batch_05` | `2_high_cross_system_coverage` | `heavy` | 87 | 24 | 43 | 43 | 0 | `ReRouteTMI` |
| 49 | `ATCSCC-GOLD-065` | `batch_07` | `2_high_cross_system_coverage` | `heavy` | 81 | 22 | 40 | 40 | 0 | `TrafficManagementInitiative` |
| 50 | `ATCSCC-GOLD-081` | `batch_09` | `2_high_cross_system_coverage` | `heavy` | 75 | 22 | 37 | 37 | 0 | `GroundDelayProgramTMI` |
| 51 | `ATCSCC-GOLD-091` | `batch_10` | `2_high_cross_system_coverage` | `heavy` | 67 | 20 | 33 | 33 | 0 | `GroundStopTMI` |
| 52 | `ATCSCC-GOLD-064` | `batch_07` | `3_standard_review` | `medium` | 65 | 19 | 32 | 32 | 0 | `TrafficManagementInitiative` |
| 53 | `ATCSCC-GOLD-073` | `batch_08` | `3_standard_review` | `medium` | 65 | 19 | 32 | 32 | 0 | `GroundStopTMI` |
| 54 | `ATCSCC-GOLD-074` | `batch_08` | `3_standard_review` | `medium` | 65 | 19 | 32 | 32 | 0 | `TrafficManagementInitiative` |
| 55 | `ATCSCC-GOLD-038` | `batch_04` | `3_standard_review` | `medium` | 63 | 19 | 31 | 31 | 0 | `GroundDelayProgramTMI` |
| 56 | `ATCSCC-GOLD-084` | `batch_09` | `3_standard_review` | `medium` | 63 | 19 | 31 | 31 | 0 | `ReRouteTMI` |
| 57 | `ATCSCC-GOLD-100` | `batch_10` | `3_standard_review` | `medium` | 61 | 18 | 30 | 30 | 0 | `TrafficManagementInitiative` |
| 58 | `ATCSCC-GOLD-050` | `batch_05` | `3_standard_review` | `medium` | 59 | 18 | 29 | 29 | 0 | `TrafficManagementInitiative` |
| 59 | `ATCSCC-GOLD-077` | `batch_08` | `3_standard_review` | `medium` | 59 | 18 | 29 | 29 | 0 | `TrafficManagementInitiative` |
| 60 | `ATCSCC-GOLD-045` | `batch_05` | `3_standard_review` | `medium` | 57 | 17 | 28 | 28 | 0 | `ReRouteTMI` |
| 61 | `ATCSCC-GOLD-061` | `batch_07` | `3_standard_review` | `medium` | 57 | 17 | 28 | 28 | 0 | `TrafficManagementInitiative` |
| 62 | `ATCSCC-GOLD-072` | `batch_08` | `3_standard_review` | `medium` | 57 | 16 | 28 | 28 | 0 | `TrafficManagementInitiative` |
| 63 | `ATCSCC-GOLD-041` | `batch_05` | `3_standard_review` | `medium` | 55 | 16 | 27 | 27 | 0 | `ReRouteTMI` |
| 64 | `ATCSCC-GOLD-067` | `batch_07` | `3_standard_review` | `medium` | 55 | 17 | 27 | 27 | 0 | `TrafficManagementInitiative` |
| 65 | `ATCSCC-GOLD-068` | `batch_07` | `3_standard_review` | `medium` | 55 | 16 | 27 | 27 | 0 | `TrafficManagementInitiative` |
| 66 | `ATCSCC-GOLD-093` | `batch_10` | `3_standard_review` | `medium` | 55 | 17 | 27 | 27 | 0 | `GroundDelayProgramTMI` |
| 67 | `ATCSCC-GOLD-062` | `batch_07` | `3_standard_review` | `medium` | 53 | 17 | 26 | 26 | 0 | `TrafficManagementInitiative` |
| 68 | `ATCSCC-GOLD-086` | `batch_09` | `3_standard_review` | `medium` | 53 | 17 | 26 | 26 | 0 | `TrafficManagementInitiative` |
| 69 | `ATCSCC-GOLD-088` | `batch_09` | `3_standard_review` | `medium` | 53 | 16 | 26 | 26 | 0 | `GroundDelayProgramTMI` |
| 70 | `ATCSCC-GOLD-042` | `batch_05` | `3_standard_review` | `medium` | 51 | 16 | 25 | 25 | 0 | `ReRouteTMI` |
| 71 | `ATCSCC-GOLD-051` | `batch_06` | `3_standard_review` | `medium` | 51 | 17 | 25 | 25 | 0 | `TrafficManagementInitiative` |
| 72 | `ATCSCC-GOLD-071` | `batch_08` | `3_standard_review` | `medium` | 51 | 16 | 25 | 25 | 0 | `TrafficManagementInitiative` |
| 73 | `ATCSCC-GOLD-089` | `batch_09` | `3_standard_review` | `medium` | 51 | 17 | 25 | 25 | 0 | `ReRouteTMI` |
| 74 | `ATCSCC-GOLD-096` | `batch_10` | `3_standard_review` | `medium` | 51 | 17 | 25 | 25 | 0 | `TrafficManagementInitiative` |
| 75 | `ATCSCC-GOLD-034` | `batch_04` | `3_standard_review` | `medium` | 49 | 15 | 24 | 24 | 0 | `GroundDelayProgramTMI` |
| 76 | `ATCSCC-GOLD-060` | `batch_06` | `3_standard_review` | `medium` | 49 | 14 | 24 | 24 | 0 | `TrafficManagementInitiative` |
| 77 | `ATCSCC-GOLD-063` | `batch_07` | `3_standard_review` | `medium` | 49 | 14 | 24 | 24 | 0 | `TrafficManagementInitiative` |
| 78 | `ATCSCC-GOLD-079` | `batch_08` | `3_standard_review` | `medium` | 49 | 15 | 24 | 24 | 0 | `ReRouteTMI` |
| 79 | `ATCSCC-GOLD-087` | `batch_09` | `3_standard_review` | `medium` | 49 | 14 | 24 | 24 | 0 | `TrafficManagementInitiative` |
| 80 | `ATCSCC-GOLD-076` | `batch_08` | `3_standard_review` | `medium` | 47 | 14 | 23 | 23 | 0 | `TrafficManagementInitiative` |
| 81 | `ATCSCC-GOLD-083` | `batch_09` | `3_standard_review` | `medium` | 47 | 14 | 23 | 23 | 0 | `GroundStopTMI` |
| 82 | `ATCSCC-GOLD-078` | `batch_08` | `3_standard_review` | `medium` | 45 | 15 | 22 | 22 | 0 | `TrafficManagementInitiative` |
| 83 | `ATCSCC-GOLD-075` | `batch_08` | `3_standard_review` | `medium` | 43 | 15 | 21 | 21 | 0 | `TrafficManagementInitiative` |
| 84 | `ATCSCC-GOLD-049` | `batch_05` | `3_standard_review` | `medium` | 41 | 14 | 20 | 20 | 0 | `TrafficManagementInitiative` |
| 85 | `ATCSCC-GOLD-066` | `batch_07` | `3_standard_review` | `medium` | 41 | 14 | 20 | 20 | 0 | `TrafficManagementInitiative` |
| 86 | `ATCSCC-GOLD-069` | `batch_07` | `3_standard_review` | `medium` | 41 | 13 | 20 | 20 | 0 | `TrafficManagementInitiative` |
| 87 | `ATCSCC-GOLD-094` | `batch_10` | `3_standard_review` | `medium` | 41 | 14 | 20 | 20 | 0 | `TrafficManagementInitiative` |
| 88 | `ATCSCC-GOLD-033` | `batch_04` | `3_standard_review` | `light` | 39 | 13 | 19 | 19 | 0 | `GroundDelayProgramTMI` |
| 89 | `ATCSCC-GOLD-043` | `batch_05` | `3_standard_review` | `light` | 39 | 13 | 19 | 19 | 0 | `ReRouteTMI` |
| 90 | `ATCSCC-GOLD-047` | `batch_05` | `3_standard_review` | `light` | 39 | 14 | 19 | 19 | 0 | `TrafficManagementInitiative` |
| 91 | `ATCSCC-GOLD-070` | `batch_07` | `3_standard_review` | `light` | 39 | 14 | 19 | 19 | 0 | `TrafficManagementInitiative` |
| 92 | `ATCSCC-GOLD-080` | `batch_08` | `3_standard_review` | `light` | 39 | 13 | 19 | 19 | 0 | `TrafficManagementInitiative` |
| 93 | `ATCSCC-GOLD-090` | `batch_09` | `3_standard_review` | `light` | 39 | 13 | 19 | 19 | 0 | `ReRouteTMI` |
| 94 | `ATCSCC-GOLD-099` | `batch_10` | `3_standard_review` | `light` | 39 | 13 | 19 | 19 | 0 | `TrafficManagementInitiative` |
| 95 | `ATCSCC-GOLD-046` | `batch_05` | `3_standard_review` | `light` | 35 | 12 | 17 | 17 | 0 | `TrafficManagementInitiative` |
| 96 | `ATCSCC-GOLD-085` | `batch_09` | `3_standard_review` | `light` | 35 | 13 | 17 | 17 | 0 | `TrafficManagementInitiative` |
| 97 | `ATCSCC-GOLD-095` | `batch_10` | `3_standard_review` | `light` | 35 | 12 | 17 | 17 | 0 | `ReRouteTMI` |
| 98 | `ATCSCC-GOLD-048` | `batch_05` | `3_standard_review` | `light` | 33 | 11 | 16 | 16 | 0 | `TrafficManagementInitiative` |
| 99 | `ATCSCC-GOLD-040` | `batch_04` | `3_standard_review` | `light` | 31 | 11 | 15 | 15 | 0 | `ReRouteTMI` |
| 100 | `ATCSCC-GOLD-097` | `batch_10` | `3_standard_review` | `light` | 27 | 11 | 13 | 13 | 0 | `ReRouteTMI` |

## Completion Gate

- All 100 records still need source-reviewed decisions before semantic scoring; this workload plan only prioritizes manual review and does not create gold truth.
