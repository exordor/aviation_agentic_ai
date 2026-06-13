# ATCSCC Profile Extension v2: Before/After Comparison

Profile extension: added `"staffing"` to the `impactingCondition` runtime enum
(`GroundDelayProgramTMI`, `GroundStopTMI`) and re-adjudicated the 8 STAFFING gold
records from `profile_gap` rejections to `valid_facts`. See
`reports/stages/atcscc_profile_extension_finding.md` for the finding.

## Gold set (deterministic, exact)

| Metric                                  | Before | After | Δ |
|-----------------------------------------|--------|-------|---|
| `valid_facts` total                     | 462    | 470   | +8 |
| `valid_facts` with predicate=`impactingCondition` | 19 | 27 | +8 |
| `rejected_fact_adjudications` for `impactingCondition` | 8 | 0 | −8 |
| Reviewed records                        | 100    | 100   | 0 |

Only the 8 listed records changed; the other 92 lines are byte-identical. Each
re-adjudication (a) moved the staffing fact into `valid_facts` with
`value="staffing"`, `extraction_method="profile_extension_staffing_v2"`,
`review_status="profile_extension_accepted"`, and (b) flipped the candidate's
embedded `validator_results` entry from `accepted=false` /
`status="rejected_schema"` to `accepted=true` / `status="repaired_accepted"` so
the record's rejection set still matches the validator.

## S4 formal experiment scoring (semantic, target-schema)

Source: `reports/stages/nasa_atmonto_formal_experiment_scoring.json`
(`S4_hybrid_backbone_enrichment.semantic_metrics`).

| Metric   | Before        | After         | Δ        |
|----------|---------------|---------------|----------|
| Precision| 0.7167883212  | 0.6794520548  | −0.0373  |
| Recall   | 0.7636080871  | 0.7619047619  | −0.0017  |
| F1       | 0.7394578313  | 0.7183200579  | −0.0211  |
| Predicted facts | 685    | 730           | +45      |
| Gold facts      | 643    | 651           | +8       |
| True positives  | 491    | 496           | +5       |
| False positives | 194    | 234           | +40      |
| False negatives | 152    | 155           | +3       |

### `impactingCondition` property-level slice

| Metric   | Before        | After         | Δ        |
|----------|---------------|---------------|----------|
| Precision| 0.5833333333  | 0.5384615384  | −0.0449  |
| Recall   | 0.9545454545  | 0.7000000000  | −0.2545  |
| F1       | 0.7241379310  | 0.6086956522  | −0.1154  |
| Predicted| 36            | 39            | +3       |
| Gold     | 22            | 30            | +8       |
| TP       | 21            | 21            | 0        |
| FP       | 15            | 18            | +3       |
| FN       | 1             | 9             | +8       |

## Which metrics changed and why

1. **Gold side (clean, deterministic):** +8 `impactingCondition` valid facts. Gold
   rose 643 → 651 overall and 22 → 30 at the `impactingCondition` predicate. This is
   the intended, isolated effect of the extension.

2. **S4 prediction side (schema-slice prompt sensitivity, reproducible):** S4
   regenerates its LLM enrichment from the schema slice, which now lists `staffing`
   as an allowed `impactingCondition` value. That prompt perturbation is reproducible
   across re-runs (two consecutive runs produced identical S4 numbers), but it shifts
   the LLM's full extraction, not only `impactingCondition`:
   - `initiativeComments` +17 predicted, `controlledNASelement` +11 predicted,
     `extensionProbability` +4, plus smaller deltas on `reRouteReason`,
     `reRouteType`, `implementationStatus`, `departureScope`.
   - Net: +45 predicted, of which only +5 are new TPs (`implementationStatus` +3,
     `reRouteType` +2) and +40 are FPs. Hence the precision drop.
   - On `impactingCondition` specifically the model matched **none** of the 8 new
     staffing gold facts (TP flat at 21; all 8 are FN), so `impactingCondition`
     recall fell 0.9545 → 0.7000. The model predicts staffing sparingly (+3 only) and
     those 3 are FP.

3. **Interpretation:** The gold/schema change itself is clean. The S4 precision/F1
   movement is dominated by LLM prompt-sensitivity to the edited schema slice (extra
   `initiativeComments`/`controlledNASelement` predictions), not by the staffing
   extension directly. The staffing extension actually exposes an S4 weakness: it
   under-predicts staffing even after the enum is opened.

## Pipeline gates

| Gate | Before (committed) | After gold edit only | Final (full re-adjudication) |
|------|--------------------|----------------------|------------------------------|
| Gold validation status | `ready_for_scoring` | `needs_revision` | `ready_for_scoring` |
| Gold freeze status | `frozen` | `ready_to_freeze` | `frozen` |
| Formal scoring status | `scored` | `pending_required_inputs` | `scored` |
| Review-decision audit | `ready_to_apply` (all 100) | `needs_revision` (8 records) | `ready_to_apply` (all 100) |
| SOTA `formal_scoring_scored` gate | passed | **failed** | passed |
| Thesis dashboard consistency | passed=True | (regenerated) | passed=True |

The "gold edit only" column is the state after Phase C moved the 8 staffing facts into
`valid_facts`. That alone broke four consistency layers, each of which had to be
re-aligned for the extension to be schema-valid and pipeline-clean:

1. **Embedded `validator_results`** — each record caches a candidate-validation
   snapshot that still marked staffing `accepted=false` / `status="rejected_schema"`.
   `validate_rejection_adjudications` requires the gold `rejected_fact_adjudications`
   to exactly match the validator-rejection set, so the 8 records flipped to
   `needs_revision`. Fix: set each staffing candidate's `validator_results` entry to
   `accepted=true` / `errors=[]` / `status="repaired_accepted"` (consistent with the
   extended enum).
2. **Gold template (source of truth)** — `freeze_reviewed_gold_set` copies the
   template to the reviewed file, so "frozen" requires reviewed ≡ template
   (`_jsonl_semantically_equal`). Fix: applied the identical re-adjudication to
   `atcscc_gold_annotation_template.jsonl`, then re-froze.
3. **Review-decision files** — `build_gold_review_decision_progress` re-applies each
   `review_decisions/batch_*.jsonl` entry to the template and re-validates. The 8
   decisions still listed staffing under `rejected_fact_adjudications`, so the audit
   flagged them `needs_revision` (this also degraded the session plan to
   `ready_for_manual_review`). Fix: in each of the 8 decision files, moved the
   staffing `impactingCondition` fact from `rejected_fact_adjudications` into
   `valid_candidate_fact_ids`. The `impactingConditionMessage` and `controlledNASelement`
   profile gaps were left untouched (separate findings, out of scope).
4. **Freeze seal** — re-running `freeze_reviewed_gold_set` stamped the new
   reviewed≡template snapshot as `frozen` (new SHA-256
   `f6684886…`).

## Test updates

Six test assertions hardcoded counts tied to the pre-extension gold; each was updated
to the post-extension value (the assertions were correct for the old profile):

- `tests/test_nasa_atmonto_formal_experiment.py`
  - S0 `semantic_metrics.gold_fact_count`: 643 → 651 (S0 `true_positive_count` stays
    462 — rule-only S0 does not emit staffing).
  - `gold_review_worklist`: `records_with_rejections` 40 → 35,
    `total_rejected_facts_to_adjudicate` 48 → 40, profile-gap suggested count 40 → 32.
  - `gold_review_workload_plan`: `records_with_rejections` 40 → 35,
    `total_rejected_facts_to_adjudicate` 48 → 40, `1_rejection_adjudication` lane 40 → 35.
  - `gold_review_priority_packets`: lanes `{40, 11, 49}` → `{35, 16, 49}`,
    first-lane record count 40 → 35.
  - `gold_review_session_plan`: session_01 `record_count` 3 → 4 and first record
    `ATCSCC-GOLD-024 / 2026-05-18:136 / batch_03` →
    `ATCSCC-GOLD-001 / 2026-05-19:032 / batch_01` (priority redistribution from the
    gold edit; `completed_session_count` stays 25, `next_session` stays `None`).
  - `gold_review_decision_progress`: `completed_rejected_fact_decision_count` 48 → 40.
- `tests/test_nasa_atmonto_experiment_protocol.py`
  - `sum(valid_facts)` over the template: 462 → 470.

`uv run ruff check .` and `uv run pytest -q` both pass (471 passed).
