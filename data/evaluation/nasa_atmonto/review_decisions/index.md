# NASA ATMONTO Gold Review Decision Templates

- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Decision directory: `data/evaluation/nasa_atmonto/review_decisions`
- Records: 100
- Batches: 10
- Suggested valid S0 candidate facts: 567

## Completion Gate

- Decision templates are editable review inputs. Applying them with all records still pending must not produce reviewed gold; set records to reviewed only after manual source-text review.
- `review_checklist` items must all be true before a record can be applied as reviewed.
- `suggested_valid_candidate_fact_ids` lists S0 facts accepted by the schema validator; copy only source-supported IDs into `valid_candidate_fact_ids`.
- Rejected-fact `suggested_*` fields are copied from `reports/stages/nasa_atmonto_rejection_adjudication.md`; leave `decision`, `rationale`, and `recommended_action` empty until a reviewer confirms them.

## Decision Files

| Batch | Samples | Records | Suggested valid S0 facts | Rejected facts | File |
| --- | --- | ---: | ---: | ---: | --- |
| `batch_01` | `ATCSCC-GOLD-001`-`ATCSCC-GOLD-010` | 10 | 74 | 14 | `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl` |
| `batch_02` | `ATCSCC-GOLD-011`-`ATCSCC-GOLD-020` | 10 | 52 | 10 | `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl` |
| `batch_03` | `ATCSCC-GOLD-021`-`ATCSCC-GOLD-030` | 10 | 76 | 13 | `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl` |
| `batch_04` | `ATCSCC-GOLD-031`-`ATCSCC-GOLD-040` | 10 | 63 | 2 | `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl` |
| `batch_05` | `ATCSCC-GOLD-041`-`ATCSCC-GOLD-050` | 10 | 41 | 0 | `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl` |
| `batch_06` | `ATCSCC-GOLD-051`-`ATCSCC-GOLD-060` | 10 | 72 | 9 | `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl` |
| `batch_07` | `ATCSCC-GOLD-061`-`ATCSCC-GOLD-070` | 10 | 44 | 0 | `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl` |
| `batch_08` | `ATCSCC-GOLD-071`-`ATCSCC-GOLD-080` | 10 | 48 | 0 | `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl` |
| `batch_09` | `ATCSCC-GOLD-081`-`ATCSCC-GOLD-090` | 10 | 48 | 0 | `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl` |
| `batch_10` | `ATCSCC-GOLD-091`-`ATCSCC-GOLD-100` | 10 | 49 | 0 | `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl` |
