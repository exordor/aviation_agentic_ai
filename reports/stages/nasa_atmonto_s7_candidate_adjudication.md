# NASA ATMONTO S7 Candidate Adjudication

## Boundary

This is deterministic project adjudication of review candidates. It is not human review and does not change the S7 main answer metrics.

## Summary

- Source LLM cases: 60
- Candidate total: 9
- Failure candidates: 3
- Strict main metrics changed: False
- Decision counts: `{'coverage_success_not_adjudicated': 6, 'profile_or_gold_boundary_case': 3}`
- Failure type counts: `{'extra_coarse_impacting_condition_for_staffing': 3}`
- Recommended policy: Keep strict S7 metrics unchanged. Treat the current failures as profile/gold-boundary review targets unless a reviewer approves either a STAFFING impactingCondition value extension or a predicate-whitelist rule for this CQ template.

## Failure Adjudications

| Review ID | Template | Source | Mode | Adjudication | Failure type | Action |
| --- | --- | --- | --- | --- | --- | --- |
| `S7-HR-001` | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:067` | `routed_token_matched_live_tfidf_graphrag` | profile_or_gold_boundary_case | extra_coarse_impacting_condition_for_staffing | unchanged |
| `S7-HR-002` | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:067` | `routed_token_matched_dense_graphrag` | profile_or_gold_boundary_case | extra_coarse_impacting_condition_for_staffing | unchanged |
| `S7-HR-003` | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:064` | `routed_token_matched_dense_graphrag` | profile_or_gold_boundary_case | extra_coarse_impacting_condition_for_staffing | unchanged |

## Details

### S7-HR-001

- Adjudication: `profile_or_gold_boundary_case`
- Failure type: `extra_coarse_impacting_condition_for_staffing`
- Would pass if extra condition ignored: `True`
- Rationale: The source supports the raw condition message STAFFING / STAFFING and the answer includes that expected value. The failure is caused by an extra coarse impactingCondition value. Current graph evidence maps the coarse value to other, while another LLM output may normalize the surface value to staffing. That mismatch is a NASA ATMONTO profile/gold boundary issue, not a retrieval miss.
- Recommended action: Do not change the main S7 score without review. Either approve STAFFING as an impactingCondition profile extension and add it to gold answer sets, or keep the CQ answer-set scoped to impactingConditionMessage and enforce a predicate whitelist for this template.

### S7-HR-002

- Adjudication: `profile_or_gold_boundary_case`
- Failure type: `extra_coarse_impacting_condition_for_staffing`
- Would pass if extra condition ignored: `True`
- Rationale: The source supports the raw condition message STAFFING / STAFFING and the answer includes that expected value. The failure is caused by an extra coarse impactingCondition value. Current graph evidence maps the coarse value to other, while another LLM output may normalize the surface value to staffing. That mismatch is a NASA ATMONTO profile/gold boundary issue, not a retrieval miss.
- Recommended action: Do not change the main S7 score without review. Either approve STAFFING as an impactingCondition profile extension and add it to gold answer sets, or keep the CQ answer-set scoped to impactingConditionMessage and enforce a predicate whitelist for this template.

### S7-HR-003

- Adjudication: `profile_or_gold_boundary_case`
- Failure type: `extra_coarse_impacting_condition_for_staffing`
- Would pass if extra condition ignored: `True`
- Rationale: The source supports the raw condition message STAFFING / STAFFING and the answer includes that expected value. The failure is caused by an extra coarse impactingCondition value. Current graph evidence maps the coarse value to other, while another LLM output may normalize the surface value to staffing. That mismatch is a NASA ATMONTO profile/gold boundary issue, not a retrieval miss.
- Recommended action: Do not change the main S7 score without review. Either approve STAFFING as an impactingCondition profile extension and add it to gold answer sets, or keep the CQ answer-set scoped to impactingConditionMessage and enforce a predicate whitelist for this template.

## Claim Boundary

Cite this artifact as failure-analysis evidence only. Do not cite it as expert validation, operational readiness, or corrected answer accuracy.
