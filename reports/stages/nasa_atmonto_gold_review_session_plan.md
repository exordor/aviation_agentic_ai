# NASA ATMONTO Gold Review Session Plan

- Status: `ready_for_manual_review`
- Workload plan: `reports/stages/nasa_atmonto_gold_review_workload_plan.md`
- Decision progress: `data/evaluation/nasa_atmonto/gold_review_decision_progress.md`
- Target session length: 90 minutes
- Ready-to-apply records: 14
- Remaining records: 86
- Estimated remaining review time: 1438 minutes
- Completed sessions: 4 / 22

## Completion Gate

- Session plans are manual-review queues only. A record becomes gold only after the reviewer confirms decisions in review_decisions JSONL, applies the draft, validates annotations, and freezes the reviewed gold set.

## Next Session

- Session: `session_05`
- Status: `pending_manual_review`
- Records: 4
- Ready / remaining records: 0 / 4
- Estimated minutes: 87
- Pending rejected-fact decisions: 4

| Order | Sample | Source | Status | Batch | Lane | Est. min | Rejected pending | Decision file | Priority packet |
| ---: | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | `ATCSCC-GOLD-030` | `2026-05-16:027` | `not_started` | `batch_03` | `1_rejection_adjudication` | 23 | 1 | `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |
| 2 | `ATCSCC-GOLD-012` | `2026-05-18:053` | `not_started` | `batch_02` | `1_rejection_adjudication` | 21 | 1 | `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |
| 3 | `ATCSCC-GOLD-057` | `2026-05-14:007` | `not_started` | `batch_06` | `1_rejection_adjudication` | 22 | 1 | `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |
| 4 | `ATCSCC-GOLD-052` | `2026-05-20:119` | `not_started` | `batch_06` | `1_rejection_adjudication` | 21 | 1 | `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl` | `data/evaluation/nasa_atmonto/review_priority_packets/1_rejection_adjudication.md` |

## Sessions

| Session | Status | Records | Ready | Remaining | Est. min | Rejected facts | Pending rejected decisions | Lanes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `session_01` | `ready_to_apply` | 4 | 4 | 0 | 85 | 8 | 0 | `{"1_rejection_adjudication": 4}` |
| `session_02` | `ready_to_apply` | 4 | 4 | 0 | 74 | 8 | 0 | `{"1_rejection_adjudication": 4}` |
| `session_03` | `ready_to_apply` | 3 | 3 | 0 | 72 | 3 | 0 | `{"1_rejection_adjudication": 3}` |
| `session_04` | `ready_to_apply` | 3 | 3 | 0 | 69 | 3 | 0 | `{"1_rejection_adjudication": 3}` |
| `session_05` | `pending_manual_review` | 4 | 0 | 4 | 87 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_06` | `pending_manual_review` | 4 | 0 | 4 | 83 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_07` | `pending_manual_review` | 4 | 0 | 4 | 83 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_08` | `pending_manual_review` | 4 | 0 | 4 | 78 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_09` | `pending_manual_review` | 4 | 0 | 4 | 74 | 4 | 4 | `{"1_rejection_adjudication": 4}` |
| `session_10` | `pending_manual_review` | 5 | 0 | 5 | 89 | 5 | 5 | `{"1_rejection_adjudication": 5}` |
| `session_11` | `pending_manual_review` | 4 | 0 | 4 | 87 | 1 | 1 | `{"1_rejection_adjudication": 1, "2_high_cross_system_coverage": 3}` |
| `session_12` | `pending_manual_review` | 4 | 0 | 4 | 89 | 0 | 0 | `{"2_high_cross_system_coverage": 4}` |
| `session_13` | `pending_manual_review` | 4 | 0 | 4 | 75 | 0 | 0 | `{"3_standard_review": 4}` |
| `session_14` | `pending_manual_review` | 5 | 0 | 5 | 87 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_15` | `pending_manual_review` | 5 | 0 | 5 | 80 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_16` | `pending_manual_review` | 5 | 0 | 5 | 79 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_17` | `pending_manual_review` | 5 | 0 | 5 | 76 | 0 | 0 | `{"3_standard_review": 5}` |
| `session_18` | `pending_manual_review` | 6 | 0 | 6 | 88 | 0 | 0 | `{"3_standard_review": 6}` |
| `session_19` | `pending_manual_review` | 6 | 0 | 6 | 80 | 0 | 0 | `{"3_standard_review": 6}` |
| `session_20` | `pending_manual_review` | 7 | 0 | 7 | 89 | 0 | 0 | `{"3_standard_review": 7}` |
| `session_21` | `pending_manual_review` | 7 | 0 | 7 | 84 | 0 | 0 | `{"3_standard_review": 7}` |
| `session_22` | `pending_manual_review` | 3 | 0 | 3 | 30 | 0 | 0 | `{"3_standard_review": 3}` |
