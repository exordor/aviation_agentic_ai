# ATCSCC Profile Extension Finding: STAFFING Impacting Condition

## Discovery

During S7 human review of the 60-case answer-generation sample, three CAUSE-CONDITION
cases (S7-BR-013, S7-BR-043, S7-BR-045) were flagged incorrect because the LLM returned
an `impactingCondition` predicate value not in the expected answer set. Root-cause tracing
showed the issue was NOT a model error but a profile gap: the NASA ATMONTO
`impactingCondition` enum (equipment/other/runway/volume/weather) lacks a STAFFING
category that recurs across ATCSCC advisories.

## Evidence of Systematic Gap

- 8 of 100 reviewed gold records have `impactingCondition` facts rejected as `profile_gap`
  with `allowed_value_violation`.
- All 8 have identical evidence: "IMPACTING CONDITION: STAFFING / STAFFING".
- The gold reviewer's adjudication explicitly recommended: "Review a STAFFING profile
  extension or preserve STAFFING as raw evidence before accepting this pattern as
  schema-valid gold."
- STAFFING is an operational/personnel condition (air traffic controller staffing),
  distinct from the physical/technical categories (weather/volume/runway/equipment) in
  the original NASA ATMONTO enum.

## Extension

Add `"staffing"` to the `allowed_values` for `impactingCondition` on
`GroundDelayProgramTMI` and `GroundStopTMI` in the runtime profile (catalog + schema
slice). Re-adjudicate the 8 affected gold records: their `impactingCondition` fact moves
from `rejected_fact_adjudications` (profile_gap) to `valid_facts` with value "staffing".

## Affected Records

- 2026-05-19:079, 2026-05-19:074, 2026-05-15:067, 2026-05-15:084,
  2026-05-14:089, 2026-05-15:064, 2026-05-20:163, 2026-05-18:136

## Claim Boundary

This is a source-native profile extension discovered through the extraction and review
process. It makes the profile more faithful to real ATCSCC operational semantics. It does
not claim NASA ATMONTO is incomplete as a general ontology, only that ATCSCC advisories
use a recurring condition category the reference vocabulary did not model.
