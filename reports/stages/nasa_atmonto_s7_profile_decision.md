# NASA ATMONTO S7 Profile Decision What-If

## Boundary

This report converts deterministic S7 candidate adjudication into a profile-policy sensitivity analysis. It does not modify the NASA ATMONTO profile, gold labels, S7 main metrics, or generated answers.

## Decision Summary

- Boundary adjudications: 3
- Corrected records under what-if: 3
- Strict main metrics changed: False
- Gold or profile changed: False
- What-if metrics replace main metrics: False
- Recommended policy: Keep strict S7 metrics unchanged. Report the predicate-whitelist what-if as a sensitivity analysis, and treat STAFFING as a proposed profile extension that requires human or supervisor approval before changing gold/profile artifacts.

## Strict vs What-If Metrics

| Mode | Strict correctness | What-if correctness | Strict unsupported claim rate | What-if unsupported claim rate | Corrected records |
| --- | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 0.9667 | 1 | 0.0167 | 0 | 1 |
| `routed_token_matched_dense_graphrag` | 0.9333 | 1 | 0.0333 | 0 | 2 |

## Decision Options

| Option | Status | Main metric action | Required follow-up |
| --- | --- | --- | --- |
| `predicate_whitelist_current_profile` | recommended_for_reporting | unchanged | Use as a sensitivity analysis in the thesis; do not replace strict main S7 metrics. |
| `staffing_profile_extension_proposal` | requires_human_or_supervisor_review | not_applied | Review ATCSCC source frequency, profile semantics, and NASA ATMONTO alignment before changing ontology/profile/gold artifacts. |

## Case Decisions

| Review ID | Source | Mode | Failure type | Profile policy | Profile extension |
| --- | --- | --- | --- | --- | --- |
| `S7-HR-001` | `2026-05-15:067` | `routed_token_matched_live_tfidf_graphrag` | extra_coarse_impacting_condition_for_staffing | what_if_only | proposed_not_applied |
| `S7-HR-002` | `2026-05-15:067` | `routed_token_matched_dense_graphrag` | extra_coarse_impacting_condition_for_staffing | what_if_only | proposed_not_applied |
| `S7-HR-003` | `2026-05-15:064` | `routed_token_matched_dense_graphrag` | extra_coarse_impacting_condition_for_staffing | what_if_only | proposed_not_applied |

## Claim Boundary

Cite this as profile-decision sensitivity evidence only. It is not human review, not a gold-label update, and not proof that NASA ATMONTO already contains STAFFING as an approved impactingCondition value.
