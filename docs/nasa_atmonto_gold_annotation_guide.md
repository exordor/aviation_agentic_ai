# NASA ATMONTO ATCSCC Gold Annotation Guide

## Material Passport

- Artifact: annotation guide for the NASA ATMONTO ATCSCC formal experiment.
- Applies to: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Cross-system checklist:
  `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.jsonl`
- Batch review index: `data/evaluation/nasa_atmonto/review_batches/index.md`
- Decision templates: `data/evaluation/nasa_atmonto/review_decisions/index.md`
- Decision progress:
  `data/evaluation/nasa_atmonto/gold_review_decision_progress.md`
- Progress tracker: `data/evaluation/nasa_atmonto/gold_review_progress.md`
- Workload plan: `reports/stages/nasa_atmonto_gold_review_workload_plan.md`
- Priority packets: `data/evaluation/nasa_atmonto/review_priority_packets/index.md`
- Validation command: `uv run python scripts/validate_nasa_atmonto_gold_annotations.py`
- Boundary: this guide creates a retrospective research gold set. It does not
  support live aviation operations, flight planning, ATC decisions, or safety
  certification.

## Annotation Goal

Each sampled ATCSCC advisory needs a reviewed gold annotation so S0-S3 can be
scored on the same 100 records. The gold set is the evaluation target for
triple precision, recall, F1, and manual semantic correctness. NASA ATMONTO is
the schema constraint, not the ground truth by itself.

## Record Status

Use one of these statuses:

- `pending_manual_gold_annotation`: not ready for scoring.
- `reviewed`: ready for automated validation and scoring.

A record should become `reviewed` only after all valid facts, invalid candidate
facts, missing facts, and rejected-fact adjudications have been checked.

## Fact Fields

Gold facts should use the same canonical shape as system predictions:

- `fact_type`: `object_property` or `datatype_property`
- `subject`: subject URI when available
- `subject_class`: NASA ATMONTO class or compact local class name
- `predicate`: NASA ATMONTO property or compact local property name
- `object`: object URI or identifier for object-property facts
- `object_class`: object class for object-property facts
- `value`: literal value for datatype-property facts
- `datatype`: datatype for datatype-property facts
- `evidence_text`: exact or whitespace-normalized excerpt from `source_text`
- `source_id`: must match the record source ID

For every reviewed record, put correct extracted facts in `valid_facts`. Put
gold facts missed by all systems or by the candidate baseline in
`missing_facts`.

Use `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.jsonl` as a
coverage checklist after reading the source text. It aggregates S0-S3 candidate
facts and validator outcomes, but it is not gold truth; source evidence and this
guide remain authoritative for the final annotation.

For review ergonomics, use
`data/evaluation/nasa_atmonto/review_batches/index.md` to work through ten
10-record Markdown batches. The batch files are checklists only; transfer final
decisions back into the JSONL template before validation.

Use `reports/stages/nasa_atmonto_gold_review_workload_plan.md` before starting
manual review. It groups the 100 advisories into priority lanes based on
validator rejections, cross-system candidate alternatives, and batch workload.
The workload plan is only a queue planner; it does not create gold truth.

Use `data/evaluation/nasa_atmonto/review_priority_packets/index.md` for the
actual priority-ordered review packets. These packets put source excerpts,
candidate facts, copyable S0/S1-S3 fact IDs, and rejected-fact adjudication
items in the same Markdown page. Final decisions still belong in the JSONL
files under `data/evaluation/nasa_atmonto/review_decisions/`.

For structured entry, edit the JSONL files under
`data/evaluation/nasa_atmonto/review_decisions/`, then run
`uv run python scripts/apply_nasa_atmonto_gold_review_decisions.py` to produce a
reviewed-draft gold template for validation.

While editing those JSONL files, run
`uv run python scripts/prepare_nasa_atmonto_gold_review_decision_progress.py`
to audit decision-level progress before applying the draft. This catches
records that are still pending, missing rejected-fact decisions, or contain
unknown candidate IDs.

Decision templates include `suggested_valid_candidate_fact_ids` for S0 facts
that passed schema validation. These are copy aids only: copy an ID into
`valid_candidate_fact_ids` only after checking that the fact is supported by the
source text.

Rejected-fact adjudication entries include `suggested_decision`,
`suggested_rationale`, and `suggested_recommended_action` copied from the
property-level rejection adjudication report. These are review aids only:
copy or edit them into `decision`, `rationale`, and `recommended_action` after
checking the source evidence.

Decision files support two accepted-fact paths:

- `valid_candidate_fact_ids`: S0 rule-baseline candidate IDs copied into
  `valid_facts`.
- `valid_cross_system_fact_ids`: schema-valid S1-S3 candidate IDs copied into
  `missing_facts` with `source_system_id` provenance. Use this only after
  checking the source text; the cross-system package is a checklist, not truth.

Free-form or corrected facts that cannot be copied directly from S0-S3 should
still be entered manually in `missing_facts`.

After each batch update, run
`uv run python scripts/prepare_nasa_atmonto_gold_review_decision_progress.py`
to check the editable decision files, then run
`uv run python scripts/prepare_nasa_atmonto_gold_review_progress.py` to refresh
the batch-level progress report and confirm whether the gold set can be frozen.

## Invalid Candidate Facts

Put candidate `fact_id` values judged semantically wrong in
`invalid_candidate_fact_ids`. These IDs must come from the record's
`candidate_facts` list.

Validator acceptance is not semantic truth. A structurally accepted candidate can
still be invalid if the object, predicate, value, or evidence does not match the
advisory meaning.

## Rejected-Fact Adjudication

For each validator-rejected fact in a reviewed record, add a
`rejected_fact_adjudications` entry:

```json
{
  "fact_id": "fact-example",
  "decision": "profile_gap",
  "rationale": "The source supports the value, but the current ATMONTO runtime profile lacks the needed class/range/enum coverage.",
  "recommended_action": "Review profile extension before accepting this pattern."
}
```

Allowed decisions:

- `extractor_bug`: the extractor normalized, typed, or parsed the source
  incorrectly.
- `profile_gap`: the source supports the fact, but the current NASA ATMONTO
  runtime profile is too narrow for this ATCSCC pattern.
- `source_ambiguity`: the advisory text is not clear enough for a stable fact.
- `manual_review_only`: keep as reviewed evidence but do not change extractor or
  profile yet.

This is the manual bridge from the 288 pilot rejections to property-level
engineering decisions.

## Validation Gate

Run:

```bash
uv run python scripts/validate_nasa_atmonto_gold_annotations.py
```

The gold set is usable for formal scoring only when the validation report status
is `ready_for_scoring`. The current template is expected to report
`pending_manual_annotation` until the 100 records are manually reviewed.
