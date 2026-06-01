# NASA ATMONTO Gold Review Session Plan

- Status: `ready_for_manual_review`
- Workload plan: `reports/stages/nasa_atmonto_gold_review_workload_plan.md`
- Decision progress: `data/evaluation/nasa_atmonto/gold_review_decision_progress.md`
- Target session length: 90 minutes
- Remaining records: 100
- Estimated remaining review time: 1738 minutes
- Sessions: 22

## Completion Gate

- Session plans are manual-review queues only. A record becomes gold only after the reviewer confirms decisions in review_decisions JSONL, applies the draft, validates annotations, and freezes the reviewed gold set.

## Next Session

- Session: `session_01`
- Records: 4
- Estimated minutes: 85
- Pending rejected-fact decisions: 8

| Order | Sample | Source | Batch | Lane | Est. min | Rejected pending | Decision file | Priority packet |
| ---: | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | `ATCSCC-GOLD-024` | `2026-05-18:136` | `batch_03` | `1_rejection_adjudication` | 23 | 2 | `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |
| 2 | `ATCSCC-GOLD-023` | `2026-05-20:163` | `batch_03` | `1_rejection_adjudication` | 22 | 2 | `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |
| 3 | `ATCSCC-GOLD-005` | `2026-05-19:059` | `batch_01` | `1_rejection_adjudication` | 20 | 2 | `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |
| 4 | `ATCSCC-GOLD-001` | `2026-05-19:032` | `batch_01` | `1_rejection_adjudication` | 20 | 2 | `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |

## Sessions

| Session | Records | Est. min | Rejected facts | Pending rejected decisions | Lanes |
| --- | ---: | ---: | ---: | ---: | --- |
| `session_01` | 4 | 85 | 8 | 8 | `{"1_rejection_adjudication": 4}` |
| `session_02` | 4 | 74 | 8 | 8 | `{"1_rejection_adjudication": 4}` |
| `session_03` | 3 | 72 | 3 | 3 | `{"1_rejection_adjudication": 3}` |
| `session_04` | 3 | 69 | 3 | 3 | `{"1_rejection_adjudication": 3}` |
| `session_05` | 4 | 87 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_06` | 4 | 83 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_07` | 4 | 83 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_08` | 4 | 78 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_09` | 4 | 74 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_10` | 5 | 89 | 5 | 5 | `{"1_rejection_adjudication": 5}` |
| `session_11` | 4 | 87 | 1 | 1 | `{"1_rejection_adjudication": 1, "2_high_cross_system_coverage": 3}` |
| `session_12` | 4 | 89 | 0 | 0 | `{"2_high_cross_system_coverage": 4}` |
| `session_13` | 4 | 75 | 0 | 0 | `{"3_standard_review": 4}` |
| `session_14` | 5 | 87 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_15` | 5 | 80 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_16` | 5 | 79 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_17` | 5 | 76 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_18` | 6 | 88 | 0 | 0 | `{"3_standard_review": 6}` |
| `session_19` | 6 | 80 | 0 | 0 | `{"3_standard_review": 6}` |
| `session_20` | 7 | 89 | 0 | 0 | `{"3_standard_review": 7}` |
| `session_21` | 7 | 84 | 0 | 0 | `{"3_standard_review": 7}` |
| `session_22` | 3 | 30 | 0 | 0 | `{"3_standard_review": 3}` |
