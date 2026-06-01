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
- Estimated total review time: 1738 minutes (28.97 hours)
- Complexity counts: `{"heavy": 18, "light": 21, "medium": 61}`
- Priority lanes: `{"1_rejection_adjudication": 40, "2_high_cross_system_coverage": 7, "3_standard_review": 53}`

## Priority Lanes

| Lane | Meaning |
| --- | --- |
| `1_rejection_adjudication` | Review first: these records need both semantic gold decisions and rejected-fact adjudications. |
| `2_high_cross_system_coverage` | Review next: no pilot rejection, but many cross-system candidate alternatives need source checks. |
| `3_standard_review` | Complete after the higher-workload lanes; still required for final recall/F1. |

## Batch Workload

| Batch | Samples | Records | Clusters | Cross-system clusters | Rejected facts | Est. min | Complexity | Lanes | File |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `batch_01` | `ATCSCC-GOLD-001`-`ATCSCC-GOLD-010` | 10 | 282 | 201 | 14 | 185 | `{"heavy": 1, "light": 1, "medium": 8}` | `{"1_rejection_adjudication": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_01.md` |
| `batch_02` | `ATCSCC-GOLD-011`-`ATCSCC-GOLD-020` | 10 | 356 | 298 | 10 | 218 | `{"heavy": 5, "medium": 5}` | `{"1_rejection_adjudication": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_02.md` |
| `batch_03` | `ATCSCC-GOLD-021`-`ATCSCC-GOLD-030` | 10 | 324 | 246 | 13 | 209 | `{"heavy": 3, "medium": 7}` | `{"1_rejection_adjudication": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_03.md` |
| `batch_04` | `ATCSCC-GOLD-031`-`ATCSCC-GOLD-040` | 10 | 312 | 254 | 2 | 181 | `{"heavy": 3, "light": 2, "medium": 5}` | `{"1_rejection_adjudication": 2, "2_high_cross_system_coverage": 3, "3_standard_review": 5}` | `data/evaluation/nasa_atmonto/review_batches/batch_04.md` |
| `batch_05` | `ATCSCC-GOLD-041`-`ATCSCC-GOLD-050` | 10 | 233 | 193 | 0 | 142 | `{"heavy": 1, "light": 5, "medium": 4}` | `{"2_high_cross_system_coverage": 1, "3_standard_review": 9}` | `data/evaluation/nasa_atmonto/review_batches/batch_05.md` |
| `batch_06` | `ATCSCC-GOLD-051`-`ATCSCC-GOLD-060` | 10 | 299 | 235 | 9 | 187 | `{"heavy": 2, "light": 1, "medium": 7}` | `{"1_rejection_adjudication": 8, "3_standard_review": 2}` | `data/evaluation/nasa_atmonto/review_batches/batch_06.md` |
| `batch_07` | `ATCSCC-GOLD-061`-`ATCSCC-GOLD-070` | 10 | 255 | 219 | 0 | 155 | `{"heavy": 1, "light": 3, "medium": 6}` | `{"2_high_cross_system_coverage": 1, "3_standard_review": 9}` | `data/evaluation/nasa_atmonto/review_batches/batch_07.md` |
| `batch_08` | `ATCSCC-GOLD-071`-`ATCSCC-GOLD-080` | 10 | 242 | 200 | 0 | 146 | `{"light": 2, "medium": 8}` | `{"3_standard_review": 10}` | `data/evaluation/nasa_atmonto/review_batches/batch_08.md` |
| `batch_09` | `ATCSCC-GOLD-081`-`ATCSCC-GOLD-090` | 10 | 261 | 218 | 0 | 159 | `{"heavy": 1, "light": 3, "medium": 6}` | `{"2_high_cross_system_coverage": 1, "3_standard_review": 9}` | `data/evaluation/nasa_atmonto/review_batches/batch_09.md` |
| `batch_10` | `ATCSCC-GOLD-091`-`ATCSCC-GOLD-100` | 10 | 255 | 216 | 0 | 156 | `{"heavy": 1, "light": 4, "medium": 5}` | `{"2_high_cross_system_coverage": 1, "3_standard_review": 9}` | `data/evaluation/nasa_atmonto/review_batches/batch_10.md` |

## Recommended Review Order

| Order | Sample | Batch | Lane | Tier | Score | Est. min | Clusters | Cross-system | Rejected | Class |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `ATCSCC-GOLD-024` | `batch_03` | `1_rejection_adjudication` | `heavy` | 66 | 23 | 34 | 25 | 2 | `GroundStopTMI` |
| 2 | `ATCSCC-GOLD-023` | `batch_03` | `1_rejection_adjudication` | `medium` | 64 | 22 | 33 | 24 | 2 | `GroundStopTMI` |
| 3 | `ATCSCC-GOLD-005` | `batch_01` | `1_rejection_adjudication` | `medium` | 61 | 20 | 30 | 24 | 2 | `TrafficManagementInitiative` |
| 4 | `ATCSCC-GOLD-001` | `batch_01` | `1_rejection_adjudication` | `medium` | 58 | 20 | 32 | 19 | 2 | `ReRouteTMI` |
| 5 | `ATCSCC-GOLD-056` | `batch_06` | `1_rejection_adjudication` | `medium` | 54 | 19 | 27 | 20 | 2 | `TrafficManagementInitiative` |
| 6 | `ATCSCC-GOLD-021` | `batch_03` | `1_rejection_adjudication` | `medium` | 52 | 20 | 26 | 19 | 2 | `GroundStopTMI` |
| 7 | `ATCSCC-GOLD-007` | `batch_01` | `1_rejection_adjudication` | `medium` | 45 | 17 | 22 | 16 | 2 | `TrafficManagementInitiative` |
| 8 | `ATCSCC-GOLD-006` | `batch_01` | `1_rejection_adjudication` | `medium` | 44 | 18 | 23 | 14 | 2 | `GroundDelayProgramTMI` |
| 9 | `ATCSCC-GOLD-011` | `batch_02` | `1_rejection_adjudication` | `heavy` | 84 | 25 | 42 | 38 | 1 | `ReRouteTMI` |
| 10 | `ATCSCC-GOLD-022` | `batch_03` | `1_rejection_adjudication` | `heavy` | 80 | 24 | 41 | 35 | 1 | `GroundDelayProgramTMI` |
| 11 | `ATCSCC-GOLD-014` | `batch_02` | `1_rejection_adjudication` | `heavy` | 77 | 23 | 39 | 34 | 1 | `ReRouteTMI` |
| 12 | `ATCSCC-GOLD-010` | `batch_01` | `1_rejection_adjudication` | `heavy` | 76 | 23 | 38 | 34 | 1 | `ReRouteTMI` |
| 13 | `ATCSCC-GOLD-018` | `batch_02` | `1_rejection_adjudication` | `heavy` | 76 | 23 | 40 | 32 | 1 | `GroundDelayProgramTMI` |
| 14 | `ATCSCC-GOLD-019` | `batch_02` | `1_rejection_adjudication` | `heavy` | 72 | 23 | 37 | 31 | 1 | `GroundDelayProgramTMI` |
| 15 | `ATCSCC-GOLD-030` | `batch_03` | `1_rejection_adjudication` | `heavy` | 72 | 23 | 37 | 31 | 1 | `GroundStopTMI` |
| 16 | `ATCSCC-GOLD-012` | `batch_02` | `1_rejection_adjudication` | `heavy` | 69 | 21 | 35 | 30 | 1 | `ReRouteTMI` |
| 17 | `ATCSCC-GOLD-057` | `batch_06` | `1_rejection_adjudication` | `heavy` | 69 | 22 | 37 | 28 | 1 | `GroundStopTMI` |
| 18 | `ATCSCC-GOLD-052` | `batch_06` | `1_rejection_adjudication` | `heavy` | 67 | 21 | 34 | 29 | 1 | `GroundStopTMI` |
| 19 | `ATCSCC-GOLD-016` | `batch_02` | `1_rejection_adjudication` | `medium` | 65 | 21 | 33 | 28 | 1 | `ReRouteTMI` |
| 20 | `ATCSCC-GOLD-028` | `batch_03` | `1_rejection_adjudication` | `medium` | 65 | 21 | 35 | 26 | 1 | `GroundStopTMI` |
| 21 | `ATCSCC-GOLD-054` | `batch_06` | `1_rejection_adjudication` | `medium` | 65 | 21 | 35 | 26 | 1 | `GroundStopTMI` |
| 22 | `ATCSCC-GOLD-015` | `batch_02` | `1_rejection_adjudication` | `medium` | 64 | 20 | 32 | 28 | 1 | `ReRouteTMI` |
| 23 | `ATCSCC-GOLD-020` | `batch_02` | `1_rejection_adjudication` | `medium` | 64 | 21 | 34 | 26 | 1 | `GroundDelayProgramTMI` |
| 24 | `ATCSCC-GOLD-059` | `batch_06` | `1_rejection_adjudication` | `medium` | 64 | 20 | 34 | 26 | 1 | `TrafficManagementInitiative` |
| 25 | `ATCSCC-GOLD-027` | `batch_03` | `1_rejection_adjudication` | `medium` | 63 | 21 | 34 | 25 | 1 | `GroundStopTMI` |
| 26 | `ATCSCC-GOLD-017` | `batch_02` | `1_rejection_adjudication` | `medium` | 62 | 21 | 33 | 25 | 1 | `GroundDelayProgramTMI` |
| 27 | `ATCSCC-GOLD-013` | `batch_02` | `1_rejection_adjudication` | `medium` | 61 | 20 | 31 | 26 | 1 | `ReRouteTMI` |
| 28 | `ATCSCC-GOLD-055` | `batch_06` | `1_rejection_adjudication` | `medium` | 59 | 20 | 30 | 25 | 1 | `GroundStopTMI` |
| 29 | `ATCSCC-GOLD-032` | `batch_04` | `1_rejection_adjudication` | `medium` | 58 | 19 | 30 | 24 | 1 | `GroundStopTMI` |
| 30 | `ATCSCC-GOLD-004` | `batch_01` | `1_rejection_adjudication` | `medium` | 57 | 19 | 31 | 22 | 1 | `TrafficManagementInitiative` |
| 31 | `ATCSCC-GOLD-009` | `batch_01` | `1_rejection_adjudication` | `medium` | 57 | 19 | 29 | 24 | 1 | `ReRouteTMI` |
| 32 | `ATCSCC-GOLD-026` | `batch_03` | `1_rejection_adjudication` | `medium` | 57 | 19 | 31 | 22 | 1 | `GroundStopTMI` |
| 33 | `ATCSCC-GOLD-058` | `batch_06` | `1_rejection_adjudication` | `medium` | 55 | 18 | 28 | 23 | 1 | `GroundStopTMI` |
| 34 | `ATCSCC-GOLD-053` | `batch_06` | `1_rejection_adjudication` | `medium` | 54 | 18 | 28 | 22 | 1 | `GroundStopTMI` |
| 35 | `ATCSCC-GOLD-002` | `batch_01` | `1_rejection_adjudication` | `medium` | 53 | 18 | 29 | 20 | 1 | `TrafficManagementInitiative` |
| 36 | `ATCSCC-GOLD-025` | `batch_03` | `1_rejection_adjudication` | `medium` | 53 | 19 | 29 | 20 | 1 | `GroundStopTMI` |
| 37 | `ATCSCC-GOLD-031` | `batch_04` | `1_rejection_adjudication` | `medium` | 50 | 18 | 26 | 20 | 1 | `GroundStopTMI` |
| 38 | `ATCSCC-GOLD-008` | `batch_01` | `1_rejection_adjudication` | `medium` | 48 | 17 | 27 | 17 | 1 | `TrafficManagementInitiative` |
| 39 | `ATCSCC-GOLD-029` | `batch_03` | `1_rejection_adjudication` | `medium` | 47 | 17 | 24 | 19 | 1 | `GroundStopTMI` |
| 40 | `ATCSCC-GOLD-003` | `batch_01` | `1_rejection_adjudication` | `light` | 36 | 14 | 21 | 11 | 1 | `TrafficManagementInitiative` |
| 41 | `ATCSCC-GOLD-039` | `batch_04` | `2_high_cross_system_coverage` | `heavy` | 96 | 25 | 48 | 47 | 0 | `GroundStopTMI` |
| 42 | `ATCSCC-GOLD-098` | `batch_10` | `2_high_cross_system_coverage` | `heavy` | 93 | 25 | 48 | 44 | 0 | `ReRouteTMI` |
| 43 | `ATCSCC-GOLD-082` | `batch_09` | `2_high_cross_system_coverage` | `heavy` | 84 | 23 | 44 | 39 | 0 | `ReRouteTMI` |
| 44 | `ATCSCC-GOLD-037` | `batch_04` | `2_high_cross_system_coverage` | `heavy` | 83 | 24 | 45 | 37 | 0 | `GroundDelayProgramTMI` |
| 45 | `ATCSCC-GOLD-044` | `batch_05` | `2_high_cross_system_coverage` | `heavy` | 79 | 22 | 40 | 38 | 0 | `ReRouteTMI` |
| 46 | `ATCSCC-GOLD-036` | `batch_04` | `2_high_cross_system_coverage` | `heavy` | 75 | 22 | 41 | 33 | 0 | `GroundDelayProgramTMI` |
| 47 | `ATCSCC-GOLD-065` | `batch_07` | `2_high_cross_system_coverage` | `heavy` | 71 | 21 | 37 | 33 | 0 | `TrafficManagementInitiative` |
| 48 | `ATCSCC-GOLD-035` | `batch_04` | `3_standard_review` | `medium` | 62 | 19 | 34 | 27 | 0 | `GroundDelayProgramTMI` |
| 49 | `ATCSCC-GOLD-074` | `batch_08` | `3_standard_review` | `medium` | 62 | 18 | 32 | 29 | 0 | `TrafficManagementInitiative` |
| 50 | `ATCSCC-GOLD-081` | `batch_09` | `3_standard_review` | `medium` | 61 | 19 | 33 | 27 | 0 | `GroundDelayProgramTMI` |
| 51 | `ATCSCC-GOLD-092` | `batch_10` | `3_standard_review` | `medium` | 60 | 19 | 34 | 25 | 0 | `GroundDelayProgramTMI` |
| 52 | `ATCSCC-GOLD-064` | `batch_07` | `3_standard_review` | `medium` | 57 | 18 | 30 | 26 | 0 | `TrafficManagementInitiative` |
| 53 | `ATCSCC-GOLD-084` | `batch_09` | `3_standard_review` | `medium` | 56 | 18 | 30 | 25 | 0 | `ReRouteTMI` |
| 54 | `ATCSCC-GOLD-038` | `batch_04` | `3_standard_review` | `medium` | 55 | 17 | 31 | 23 | 0 | `GroundDelayProgramTMI` |
| 55 | `ATCSCC-GOLD-061` | `batch_07` | `3_standard_review` | `medium` | 55 | 17 | 28 | 26 | 0 | `TrafficManagementInitiative` |
| 56 | `ATCSCC-GOLD-091` | `batch_10` | `3_standard_review` | `medium` | 54 | 17 | 28 | 25 | 0 | `GroundStopTMI` |
| 57 | `ATCSCC-GOLD-100` | `batch_10` | `3_standard_review` | `medium` | 54 | 17 | 28 | 25 | 0 | `TrafficManagementInitiative` |
| 58 | `ATCSCC-GOLD-050` | `batch_05` | `3_standard_review` | `medium` | 53 | 16 | 28 | 24 | 0 | `TrafficManagementInitiative` |
| 59 | `ATCSCC-GOLD-077` | `batch_08` | `3_standard_review` | `medium` | 53 | 16 | 28 | 24 | 0 | `TrafficManagementInitiative` |
| 60 | `ATCSCC-GOLD-045` | `batch_05` | `3_standard_review` | `medium` | 50 | 16 | 27 | 22 | 0 | `ReRouteTMI` |
| 61 | `ATCSCC-GOLD-068` | `batch_07` | `3_standard_review` | `medium` | 50 | 15 | 26 | 23 | 0 | `TrafficManagementInitiative` |
| 62 | `ATCSCC-GOLD-067` | `batch_07` | `3_standard_review` | `medium` | 49 | 16 | 26 | 22 | 0 | `TrafficManagementInitiative` |
| 63 | `ATCSCC-GOLD-072` | `batch_08` | `3_standard_review` | `medium` | 49 | 15 | 26 | 22 | 0 | `TrafficManagementInitiative` |
| 64 | `ATCSCC-GOLD-096` | `batch_10` | `3_standard_review` | `medium` | 49 | 16 | 25 | 23 | 0 | `TrafficManagementInitiative` |
| 65 | `ATCSCC-GOLD-073` | `batch_08` | `3_standard_review` | `medium` | 48 | 16 | 26 | 21 | 0 | `GroundStopTMI` |
| 66 | `ATCSCC-GOLD-062` | `batch_07` | `3_standard_review` | `medium` | 47 | 16 | 25 | 21 | 0 | `TrafficManagementInitiative` |
| 67 | `ATCSCC-GOLD-086` | `batch_09` | `3_standard_review` | `medium` | 47 | 16 | 25 | 21 | 0 | `TrafficManagementInitiative` |
| 68 | `ATCSCC-GOLD-089` | `batch_09` | `3_standard_review` | `medium` | 47 | 16 | 25 | 21 | 0 | `ReRouteTMI` |
| 69 | `ATCSCC-GOLD-041` | `batch_05` | `3_standard_review` | `medium` | 46 | 15 | 25 | 20 | 0 | `ReRouteTMI` |
| 70 | `ATCSCC-GOLD-063` | `batch_07` | `3_standard_review` | `medium` | 46 | 14 | 24 | 21 | 0 | `TrafficManagementInitiative` |
| 71 | `ATCSCC-GOLD-093` | `batch_10` | `3_standard_review` | `medium` | 46 | 15 | 24 | 21 | 0 | `GroundDelayProgramTMI` |
| 72 | `ATCSCC-GOLD-051` | `batch_06` | `3_standard_review` | `medium` | 45 | 15 | 24 | 20 | 0 | `TrafficManagementInitiative` |
| 73 | `ATCSCC-GOLD-088` | `batch_09` | `3_standard_review` | `medium` | 45 | 15 | 25 | 19 | 0 | `GroundDelayProgramTMI` |
| 74 | `ATCSCC-GOLD-042` | `batch_05` | `3_standard_review` | `medium` | 44 | 14 | 24 | 19 | 0 | `ReRouteTMI` |
| 75 | `ATCSCC-GOLD-071` | `batch_08` | `3_standard_review` | `medium` | 44 | 14 | 23 | 20 | 0 | `TrafficManagementInitiative` |
| 76 | `ATCSCC-GOLD-034` | `batch_04` | `3_standard_review` | `medium` | 43 | 15 | 23 | 19 | 0 | `GroundDelayProgramTMI` |
| 77 | `ATCSCC-GOLD-079` | `batch_08` | `3_standard_review` | `medium` | 43 | 15 | 23 | 19 | 0 | `ReRouteTMI` |
| 78 | `ATCSCC-GOLD-083` | `batch_09` | `3_standard_review` | `medium` | 43 | 14 | 23 | 19 | 0 | `GroundStopTMI` |
| 79 | `ATCSCC-GOLD-076` | `batch_08` | `3_standard_review` | `medium` | 41 | 13 | 23 | 17 | 0 | `TrafficManagementInitiative` |
| 80 | `ATCSCC-GOLD-078` | `batch_08` | `3_standard_review` | `medium` | 41 | 14 | 22 | 18 | 0 | `TrafficManagementInitiative` |
| 81 | `ATCSCC-GOLD-060` | `batch_06` | `3_standard_review` | `light` | 39 | 13 | 22 | 16 | 0 | `TrafficManagementInitiative` |
| 82 | `ATCSCC-GOLD-087` | `batch_09` | `3_standard_review` | `light` | 39 | 13 | 21 | 17 | 0 | `TrafficManagementInitiative` |
| 83 | `ATCSCC-GOLD-066` | `batch_07` | `3_standard_review` | `light` | 38 | 13 | 20 | 17 | 0 | `TrafficManagementInitiative` |
| 84 | `ATCSCC-GOLD-075` | `batch_08` | `3_standard_review` | `light` | 38 | 13 | 20 | 17 | 0 | `TrafficManagementInitiative` |
| 85 | `ATCSCC-GOLD-049` | `batch_05` | `3_standard_review` | `light` | 37 | 13 | 20 | 16 | 0 | `TrafficManagementInitiative` |
| 86 | `ATCSCC-GOLD-094` | `batch_10` | `3_standard_review` | `light` | 37 | 13 | 20 | 16 | 0 | `TrafficManagementInitiative` |
| 87 | `ATCSCC-GOLD-070` | `batch_07` | `3_standard_review` | `light` | 36 | 13 | 19 | 16 | 0 | `TrafficManagementInitiative` |
| 88 | `ATCSCC-GOLD-043` | `batch_05` | `3_standard_review` | `light` | 35 | 12 | 19 | 15 | 0 | `ReRouteTMI` |
| 89 | `ATCSCC-GOLD-069` | `batch_07` | `3_standard_review` | `light` | 35 | 12 | 20 | 14 | 0 | `TrafficManagementInitiative` |
| 90 | `ATCSCC-GOLD-085` | `batch_09` | `3_standard_review` | `light` | 34 | 13 | 17 | 16 | 0 | `TrafficManagementInitiative` |
| 91 | `ATCSCC-GOLD-033` | `batch_04` | `3_standard_review` | `light` | 33 | 12 | 19 | 13 | 0 | `GroundDelayProgramTMI` |
| 92 | `ATCSCC-GOLD-047` | `batch_05` | `3_standard_review` | `light` | 33 | 13 | 18 | 14 | 0 | `TrafficManagementInitiative` |
| 93 | `ATCSCC-GOLD-080` | `batch_08` | `3_standard_review` | `light` | 33 | 12 | 19 | 13 | 0 | `TrafficManagementInitiative` |
| 94 | `ATCSCC-GOLD-090` | `batch_09` | `3_standard_review` | `light` | 33 | 12 | 18 | 14 | 0 | `ReRouteTMI` |
| 95 | `ATCSCC-GOLD-099` | `batch_10` | `3_standard_review` | `light` | 33 | 12 | 18 | 14 | 0 | `TrafficManagementInitiative` |
| 96 | `ATCSCC-GOLD-095` | `batch_10` | `3_standard_review` | `light` | 31 | 12 | 17 | 13 | 0 | `ReRouteTMI` |
| 97 | `ATCSCC-GOLD-046` | `batch_05` | `3_standard_review` | `light` | 30 | 11 | 16 | 13 | 0 | `TrafficManagementInitiative` |
| 98 | `ATCSCC-GOLD-048` | `batch_05` | `3_standard_review` | `light` | 29 | 10 | 16 | 12 | 0 | `TrafficManagementInitiative` |
| 99 | `ATCSCC-GOLD-040` | `batch_04` | `3_standard_review` | `light` | 27 | 10 | 15 | 11 | 0 | `ReRouteTMI` |
| 100 | `ATCSCC-GOLD-097` | `batch_10` | `3_standard_review` | `light` | 24 | 10 | 13 | 10 | 0 | `ReRouteTMI` |

## Completion Gate

- All 100 records still need source-reviewed decisions before semantic scoring; this workload plan only prioritizes manual review and does not create gold truth.
