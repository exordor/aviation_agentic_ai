# NASA ATMONTO ATCSCC Formal Experiment Protocol

## Material Passport

- Artifact: formal experiment protocol for the NASA ATMONTO ATCSCC KG extraction study.
- Status: protocol, reviewed 100-record gold set, S0-S3 prediction outputs,
  rejection triage, and formal scoring artifacts prepared.
- Prior stage: pilot / feasibility study.
- Pilot evidence:
  - `reports/stages/nasa_atmonto_minimal_loop_validation.md`
  - `data/ontology/curated/nasa_atmonto_schema_catalog.json`
  - `data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json`
  - `data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl`
- Formal-study inputs prepared:
  - `data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json`
  - `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
  - `data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.md`
  - `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.md`
  - `data/evaluation/nasa_atmonto/review_batches/index.md`
  - `data/evaluation/nasa_atmonto/review_decisions/index.md`
  - `data/evaluation/nasa_atmonto/gold_review_decision_progress.md`
  - `data/evaluation/nasa_atmonto/gold_review_progress.md`
  - `reports/stages/nasa_atmonto_gold_review_session_plan.md`
  - `reports/stages/nasa_atmonto_gold_semantic_groups.md`
  - `docs/nasa_atmonto_gold_annotation_guide.md`
  - `reports/stages/nasa_atmonto_gold_freeze_status.md`
  - `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
  - `data/experiments/nasa_atmonto/formal/input_records.jsonl`
  - `data/experiments/nasa_atmonto/formal/system_specs.json`
  - `data/experiments/nasa_atmonto/formal/s0_rule_only_predictions.jsonl`
  - `data/experiments/nasa_atmonto/formal/s1_llm_only_predictions.jsonl`
  - `data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_predictions.jsonl`
  - `data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_predictions.jsonl`
  - `data/experiments/nasa_atmonto/formal/s1_llm_only_prompt_batch.jsonl`
  - `data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_prompt_batch.jsonl`
  - `data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_prompt_batch.jsonl`
  - `reports/stages/nasa_atmonto_rejection_error_analysis.md`
  - `reports/stages/nasa_atmonto_rejection_adjudication.md`
  - `reports/stages/nasa_atmonto_gold_review_multiround_audit.md`
  - `reports/stages/nasa_atmonto_gold_annotation_validation.md`
  - `reports/stages/nasa_atmonto_prediction_output_validation.md`
  - `reports/stages/nasa_atmonto_formal_experiment_scoring.md`
- Claim boundary: retrospective extraction and validation research only. This protocol does not support live aviation operations, operational advisories, flight planning, dispatch, ATC decisions, or safety certification.

## Current Pilot Positioning

The current NASA ATMONTO ATCSCC loop is a pilot / feasibility study. It proves
that the local NASA OWL/XML files can be converted into a runtime schema
catalog, that an ATCSCC-focused schema slice can constrain extraction, and that a
custom validator can accept, reject, and repair candidate facts.

The pilot processed 718 ATCSCC advisory records from the aligned retrospective
window, produced 4429 candidate facts, accepted 4141 facts after structural
repair, and rejected 288 facts. The accepted facts remain
`bronze_until_reviewed`; structural validation is not semantic correctness.

The next experiment must therefore answer a stronger question:

> Does NASA ATMONTO schema-slice constrained extraction improve schema validity
> and manually judged KG extraction quality compared with rule-only and
> unconstrained LLM baselines?

## Research Claims

### C1: Runtime NASA ATMONTO Profile Feasibility

NASA ATMONTO OWL/XML can be transformed into a usable runtime schema catalog and
ATCSCC schema slice for KG extraction and validation.

- Evidence required: catalog generation succeeds; selected classes/properties
  cover ATCSCC TMI targets; missing target list is empty or explained.
- Current status: supported by the pilot.
- Limit: this is a schema engineering claim, not an extraction-accuracy claim.

### C2: Schema-Slice Constraint Benefit

An LLM using the ATCSCC schema slice should produce fewer unsupported terms and
domain/range violations than an LLM-only extractor.

- Evidence required: lower schema violation rate for `LLM + schema slice` than
  `LLM-only` on the same gold-sampled records.
- Current status: supported by the formal scoring report for schema-violation
  reduction; semantic precision/recall impact is reported descriptively and
  should not be overgeneralized beyond this 100-record retrospective sample.

### C3: Validator/Repair Benefit

Adding the validator/repair loop should improve structurally valid yield without
reducing manual semantic correctness below the LLM + schema-slice condition.

- Evidence required: repair success rate, post-repair schema violation rate, and
  manual semantic correctness on the same gold sample.
- Current status: supported on the reviewed 100-record sample: S3 improves
  structural acceptance versus S2 and does not reduce manual semantic
  correctness in the frozen-gold scoring report.

### C4: Rejection Analysis Utility

Property-level rejection analysis should separate extractor bugs from NASA
ATMONTO runtime-profile gaps.

- Evidence required: every rejection group has a reviewed action label
  (`extractor_bug`, `profile_gap`, `source_ambiguity`, or `manual_review_only`)
  and a regression or profile-extension follow-up.
- Current status: supported at property level. The finalized adjudication covers
  all 288 pilot rejections: 13 `extractor_bug` facts and 275 `profile_gap`
  facts. This does not automatically approve profile extensions or semantic gold
  facts.

## Hypotheses And Falsification Criteria

### H1: Schema Guidance Reduces Structural Drift

Compared with `LLM-only`, `LLM + schema slice` will reduce schema violation rate.

- Primary comparison: S2 vs S1.
- Falsified if S2 schema violation rate is not lower than S1 by at least 10
  percentage points, or if bootstrap confidence intervals show no practical
  separation.
- Secondary failure mode: S2 achieves lower violations only by suppressing more
  than 25 percent of gold-supported facts relative to S1.

### H2: Validator/Repair Improves Valid Yield

Compared with `LLM + schema slice`, `LLM + schema slice + validator/repair` will
increase structurally accepted facts while preserving manual semantic correctness.

- Primary comparison: S3 vs S2.
- Falsified if S3 structural repair success rate is below 15 percent of facts
  that enter the S3 validator/repair loop as initially invalid, or if S3 manual
  semantic correctness is more than 5 percentage points lower than S2.

### H3: Ontology Constraints Improve Precision More Than They Harm Recall

The validator/repair system should improve triple precision enough that any
recall loss is visible and defensible.

- Primary comparison: S3 vs S1 and S2.
- Falsified if S3 precision does not exceed S1, or if S3 F1 is lower than S1 by
  more than 5 percentage points.
- Interpretation rule: if S3 precision rises but recall drops materially, report
  the tradeoff instead of claiming a general win.

### H4: Rejection Triage Produces Actionable Engineering Decisions

Most rejected facts should be classifiable into a small set of actionable
property-level causes.

- Primary evidence: `reports/stages/nasa_atmonto_rejection_error_analysis.md`.
- Falsified if more than 20 percent of rejected facts remain
  `manual_review_required` after review, or if a proposed profile extension
  cannot be tied to source evidence and a NASA ATMONTO term.

## Gold Set Plan

The formal study uses a 100-record ATCSCC advisory sample. This is within the
requested 80-120 record range and is large enough to cover the dominant TMI
classes and current rejection modes without making manual review too heavy.

Prepared files:

- Manifest: `data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json`
- Annotation template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Review worklist: `data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.md`
- Review workload plan: `reports/stages/nasa_atmonto_gold_review_workload_plan.md`
- Review session plan: `reports/stages/nasa_atmonto_gold_review_session_plan.md`
- Review priority packets: `data/evaluation/nasa_atmonto/review_priority_packets/index.md`
- Freeze status: `reports/stages/nasa_atmonto_gold_freeze_status.md`

Current sample properties:

- Sample size: 100 advisories.
- Reviewed records: 100.
- Frozen reviewed gold:
  `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`.
- Records with at least one rejected pilot candidate: 40.
- Accepted-only pilot records: 60.
- Candidate classes:
  - `GroundDelayProgramTMI`: 16
  - `GroundStopTMI`: 21
  - `ReRouteTMI`: 23
  - `TrafficManagementInitiative`: 40
- Rejection predicate exposure:
  - `controlledNASelement`: 10
  - `extensionProbability`: 8
  - `impactingCondition`: 8
  - `impactingConditionMessage`: 17

### Semantic Stratification

The 100-record gold set is also grouped into operational semantic slices for
stratified error analysis. These groups are reporting strata, not train/dev/test
splits, and they do not create gold truth by themselves.

| Group | Records | Primary purpose |
| --- | ---: | --- |
| `ground_stop_lifecycle` | 26 | CDM ground-stop creation, extension, and cancellation behavior. |
| `reroute_or_route_constraint` | 25 | Route-required, CDR, SWAP, route-closure, and reroute-cancellation behavior. |
| `volcanic_activity_bulletin` | 19 | Volcanic bulletin extraction, especially advisory signature time versus VA DTG time. |
| `ground_delay_program_lifecycle` | 12 | GDP proposed/active/cancelled lifecycle records. |
| `airport_arrival_or_scheduling_delay` | 10 | Airport arrival-delay and scheduling-delay advisories. |
| `hotline_or_webpage_status` | 3 | Hotline/webpage activation and termination notices. |
| `airport_diversion_recovery` | 2 | Diversion-recovery activation records. |
| `special_or_flow_constraint_fyi` | 2 | Special mission or flow-constraint FYI notices. |
| `flight_plan_drop_time_status` | 1 | Extended flight-plan drop-time status. |

The authoritative grouping artifact is
`reports/stages/nasa_atmonto_gold_semantic_groups.md`; the formal scoring report
uses the same groups for per-system semantic precision/recall/F1 slices.

### Gold Annotation Task

For each sampled advisory, the reviewer records:

- valid candidate facts;
- invalid candidate fact IDs and reason;
- missing gold facts not produced by a system;
- evidence span for each valid or missing fact;
- whether a rejected fact reflects extractor behavior, source ambiguity, or a
  NASA ATMONTO runtime-profile gap.

Gold facts must use the same normalized fields for all systems:

- `subject`
- `subject_class`
- `predicate`
- `object` or literal `value`
- `object_class` when applicable
- `datatype` when applicable
- `evidence_text`
- `source_id`

For every reviewed record, validator-rejected candidate facts also need
`rejected_fact_adjudications` with one of `extractor_bug`, `profile_gap`,
`source_ambiguity`, or `manual_review_only`. The annotation guide is
`docs/nasa_atmonto_gold_annotation_guide.md`.

### Assisted Gold Adjudication Workflow

The formal gold set is human-supervised and evidence-grounded, but it does not
require the human assistant to act as an unaided aviation-domain expert. Each
review session should use an assisted adjudication workflow:

- Primary screening: Codex or a frontier model proposes accepted facts,
  rejected-fact decisions, profile-gap candidates, and missing-fact candidates
  from the source text plus S0-S3 candidate package.
- Source-evidence review: an independent reviewer checks whether every accepted
  fact has a specific advisory evidence span and whether any obvious
  source-supported fact was omitted.
- Adversarial ontology/profile review: a separate reviewer challenges
  `extractor_bug` versus `profile_gap` labels, schema-valid cross-system facts,
  proposed normalizations, and any implied NASA ATMONTO profile extension.
- User adjudication: the user reviews only unresolved conflicts, low-confidence
  calls, or proposed profile extensions, using short source snippets and
  concrete accept/revise options.

Gold truth is not created by model agreement alone. A record was marked ready only when
the final JSONL decision is source-supported, passes the semantic rubric, has no
unresolved adversarial-review issue, and has all `review_checklist` fields set to
`true`. If reviewers disagree and the source evidence does not resolve the
conflict, keep the record pending or use `source_ambiguity` /
`manual_review_only` instead of forcing a gold fact.

The review is intentionally multi-round and multi-perspective: source-only
review catches evidence overreach, ontology/profile review catches boundary
errors, and consistency review checks whether the same predicate pattern is
handled the same way across sessions. For normalized facts, the accepted value
must cite a reviewed normalization policy. In this protocol, the only approved
enum normalization is `extensionProbability:MODERATE->MEDIUM`, and it must be
entered as a corrected manual fact with `raw_value`, `value_normalization`, and a
tight source evidence span rather than accepted solely from model output.

The gold set is complete for this formal experiment after source review,
multi-perspective adjudication, validation, and freezing. The frozen reviewed
JSONL is the scoring source; future edits must create a new reviewed version
rather than silently changing reported results.

## Systems Under Test

Prepared execution files:

- Common input records: `data/experiments/nasa_atmonto/formal/input_records.jsonl`
- System specs: `data/experiments/nasa_atmonto/formal/system_specs.json`
- S0 baseline predictions: `data/experiments/nasa_atmonto/formal/s0_rule_only_predictions.jsonl`
- S1 prompt batch: `data/experiments/nasa_atmonto/formal/s1_llm_only_prompt_batch.jsonl`
- S2 prompt batch: `data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_prompt_batch.jsonl`
- S3 prompt batch: `data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_prompt_batch.jsonl`
- LLM prediction runner: `scripts/run_nasa_atmonto_llm_predictions.py`
- Saved-response reprocessor:
  `scripts/reprocess_nasa_atmonto_llm_predictions.py`
- Pending/scoring report: `reports/stages/nasa_atmonto_formal_experiment_scoring.md`
- Prediction-output validation report: `reports/stages/nasa_atmonto_prediction_output_validation.md`

These files fix the common sample, deterministic baseline, prompt batches, and
saved S1-S3 prediction outputs. The LLM outputs must come from the prediction
runner or from deterministic reprocessing of committed `raw_response` fields;
they must not be fabricated or manually filled. The prediction-output validation
report records whether every system has 100 usable records before scoring.

## Baselines And Comparators

The formal experiment uses four systems on the identical 100-record ATCSCC
sample. S0 and S1 are baselines; S2 and S3 are ontology-constrained
interventions.

| System | Role | Comparator Question |
| --- | --- | --- |
| S0 rule-only | Deterministic parser baseline | How much can a low-cost rule extractor recover before LLMs? |
| S1 LLM-only | Unconstrained LLM baseline | How much structural drift appears without ontology terms? |
| S2 LLM + schema slice | Schema-guided extraction condition | Does a compact ATCSCC slice reduce unsupported terms? |
| S3 LLM + schema slice + validator/repair | Full ontology-constrained loop | Does validation/repair improve accepted yield without semantic loss? |

### S0: Rule-Only

The existing deterministic ATCSCC extractor runs without an LLM. It uses
surface patterns and aligned time fields to produce candidate facts.

- Purpose: low-cost baseline and parser-regression target.
- Current implementation: `schema_slice_rule_baseline` in
  `src/aviation_agentic_ai/ontology/atmonto_minimal_loop.py`.
- Expected strength: high format stability and evidence anchoring.
- Expected weakness: brittle pattern matching, accepted false positives, limited recall.

### S1: LLM-Only

An LLM extracts facts from advisory text without NASA ATMONTO classes,
properties, or schema slice guidance. The output is converted into the common
fact schema for evaluation.

- Purpose: measure free-form extraction drift.
- Constraint: no ontology term list in the prompt.
- Validator role: post-hoc measurement only; no repair loop.

### S2: LLM + Schema Slice

An LLM receives only the ATCSCC schema slice, not the full NASA OWL files. It
must emit JSON in the common extraction schema.

- Purpose: test whether a compact ontology slice improves extraction.
- Constraint: use selected classes/properties from
  `data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json`.
- Validator role: post-hoc measurement only; no repair loop.

### S3: LLM + Schema Slice + Validator/Repair

The S2 output is passed through the custom validator. Invalid outputs receive one
repair opportunity with validator errors and evidence requirements.

- Purpose: test the complete ontology-constrained extraction loop.
- Repair budget: one repair attempt per invalid payload.
- Validator role: gate final structurally accepted facts and record rejected facts.

## Metrics

### JSON Adherence

Record-level percentage of system outputs that parse as JSON and match the
required payload shape.

Formula:

```text
json_adherence = valid_json_payloads / attempted_records
```

### Schema Violation Rate

Fact-level percentage of candidate facts rejected for unsupported term,
domain/range, datatype, allowed-value, or evidence anchoring errors.

Formula:

```text
schema_violation_rate = schema_rejected_facts / candidate_facts
```

### Structural Acceptance Rate

Fact-level percentage of candidate facts that pass the validator gate and are
eligible for semantic scoring. This metric is reported for every system and
must not be interpreted as repair success.

Formula:

```text
structural_acceptance_rate = structurally_accepted_facts / candidate_facts
```

### Triple Precision, Recall, And F1

Manual gold facts define the denominator. A predicted fact matches a gold fact
only when normalized subject class, predicate, object/value, datatype, and
source evidence are compatible under the annotation guide. The match key is
source-scoped: `source_id` is part of the comparison so identical fact shapes in
different advisories count as separate gold or predicted facts.

Formulas:

```text
precision = true_positive_facts / predicted_facts
recall = true_positive_facts / gold_facts
f1 = 2 * precision * recall / (precision + recall)
```

Report micro-averaged scores and property-level scores. Do not hide
property-level failures inside a single average. When reviewed gold is
available, report deterministic record-level bootstrap 95 percent confidence
intervals for precision, recall, F1, and manual semantic correctness. The
bootstrap unit is `source_id`, so the uncertainty estimate respects the
advisory-level sampling design.

### Repair Success Rate

Report repair success only for systems with an explicit repair loop, currently
S3 (`LLM + Schema Slice + Validator/Repair`). For S0-S2, this metric is
`not_applicable`; their validator pass rate is the structural acceptance rate.
When repair is enabled, report both structural and semantic repair success.

```text
structural_repair_success = repaired_accepted_facts / initially_invalid_facts
semantic_repair_success = repaired_true_positive_facts / repaired_accepted_facts
```

Structural success alone is not evidence of semantic correctness.

### Manual Semantic Correctness

Percentage of structurally accepted facts judged correct by manual review.
Correctness follows the source-evidence rubric in
`docs/nasa_atmonto_gold_annotation_guide.md`: predicate, subject/object class,
object or value, normalization, and evidence text must all match the advisory.

```text
manual_semantic_correctness = manually_correct_accepted_facts / accepted_facts
```

This metric is the guardrail against treating validator acceptance as truth.

## Rejection Error Analysis

The pilot produced 288 rejected facts. The current property-level triage groups
them as follows:

| Predicate | Error | Count | Initial decision |
| --- | --- | ---: | --- |
| `controlledNASelement` | `range_violation` | 134 | `nasa_atmonto_profile_gap_candidate` |
| `impactingConditionMessage` | `domain_violation` | 132 | `nasa_atmonto_profile_gap_candidate` |
| `extensionProbability` | `allowed_value_violation` | 13 | `extractor_normalization_bug_candidate` |
| `impactingCondition` | `allowed_value_violation` | 9 | `nasa_atmonto_profile_gap_candidate` |

The finalized property-level adjudication is stored in
`reports/stages/nasa_atmonto_rejection_adjudication.md`. It resolves the four
groups into:

- `profile_gap`: 275 facts (`controlledNASelement`, `impactingConditionMessage`,
  and `impactingCondition`).
- `extractor_bug`: 13 facts (`extensionProbability=MODERATE`, requiring a
  reviewed normalization rule before acceptance).

Property-level interpretation:

- `controlledNASelement` rejections mostly reflect ARTCC center identifiers that
  the runtime profile does not currently type as `atm:TFMcontrolElement`.
- `impactingConditionMessage` rejections mostly reflect Ground Stop advisories
  carrying detailed condition text while the current TBox domain is narrower.
- `extensionProbability=MODERATE` is likely an enum-normalization issue if
  reviewed as equivalent to `MEDIUM`.
- `impactingCondition=staffing` is a profile decision: either extend the enum or
  map to `other` while retaining the raw value.

The formal experiment must not automatically accept profile-gap candidates.
Every profile extension requires manual evidence and a regression test.

## Experimental Procedure

1. Regenerate pilot artifacts.

```bash
uv run python scripts/run_nasa_atmonto_minimal_loop.py --all-records
```

2. Regenerate gold-sample and rejection-analysis artifacts.

```bash
uv run python scripts/prepare_nasa_atmonto_experiment_protocol.py
```

3. Generate formal input records, S0 predictions, S1/S2/S3 prompt batches,
   readiness report, and the pending/scoring report.

```bash
uv run python scripts/run_nasa_atmonto_formal_experiment.py
```

4. Run S1, S2, and S3 from the prepared prompt batches on the same 100 source
   records. Use the committed S0 prediction file as the deterministic baseline.

```bash
uv run python scripts/run_nasa_atmonto_llm_predictions.py S1_llm_only --resume
uv run python scripts/run_nasa_atmonto_llm_predictions.py S2_llm_schema_slice --resume
uv run python scripts/run_nasa_atmonto_llm_predictions.py S3_llm_schema_slice_validator_repair --resume
```

For a connectivity smoke test, use `--limit 1`. Limited runs write to
`data/experiments/nasa_atmonto/formal/smoke/` by default, so they cannot
overwrite the formal S1/S2/S3 prediction files used by scoring.

5. Validate S1/S2/S3 prediction JSONL files and run metadata before scoring.

```bash
uv run python scripts/validate_nasa_atmonto_prediction_outputs.py
```

Each LLM system output must have 100 valid prediction records, one per selected
`source_id`, plus a run metadata JSON file documenting `system_id`,
`run_status`, `input_records`, and `prediction_output`.

The common output contract is a flat fact schema. Schema-slice LLMs sometimes
return a nested entity shape such as `type` plus a `properties` map. The
prediction parser normalizes this into one flat fact per property-value
assertion before validation. If the parser or normalizer changes, rebuild saved
prediction records from the committed `raw_response` fields without calling the
LLM again:

```bash
uv run python scripts/reprocess_nasa_atmonto_llm_predictions.py all
```

This reprocessing step is an adapter repair, not a new model run. It should be
reported separately from S3 validator/repair because it fixes experiment I/O
shape rather than asking the model to change its extraction.

6. Generate the cross-system candidate review package and reviewer batches.

```bash
uv run python scripts/prepare_nasa_atmonto_system_candidate_review.py
uv run python scripts/prepare_nasa_atmonto_gold_review_batches.py
uv run python scripts/prepare_nasa_atmonto_gold_review_decisions.py
uv run python scripts/prepare_nasa_atmonto_gold_review_decision_progress.py
uv run python scripts/prepare_nasa_atmonto_gold_review_progress.py
uv run python scripts/prepare_nasa_atmonto_gold_review_workload_plan.py
uv run python scripts/prepare_nasa_atmonto_gold_review_session_plan.py
uv run python scripts/prepare_nasa_atmonto_gold_review_priority_packets.py
```

Use `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.md` as a
coverage checklist during annotation. It aggregates S0-S3 candidate facts by
sample and marks validator acceptance/rejection, but it is not reviewed gold and
must not override source-text review.

The structured decision templates expose both `valid_candidate_fact_ids` for S0
rule-baseline facts and `valid_cross_system_fact_ids` for schema-valid S1-S3
facts. Applying reviewed decisions copies S0 facts into `valid_facts` and
schema-valid cross-system facts into `missing_facts` with provenance. This keeps
the gold set source-reviewed while avoiding manual retyping of correct S1-S3
candidate facts.

7. Complete manual annotation in
   `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`.
   Use `data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.md` as the
   per-record queue and
   `data/evaluation/nasa_atmonto/atcscc_system_candidate_review.jsonl` as the
   cross-system coverage checklist. The batch files under
   `data/evaluation/nasa_atmonto/review_batches/` split the 100 records into
   smaller review units. The JSONL decision templates under
   `data/evaluation/nasa_atmonto/review_decisions/` are the structured inputs
   for applying reviewed decisions.
   A record is not ready to apply as reviewed until all `review_checklist`
   fields are true: source text checked, semantic rubric checked,
   profile-gap boundary checked, and missing facts checked.

   Use `reports/stages/nasa_atmonto_gold_review_workload_plan.md` to choose
   review order. It prioritizes records needing rejected-fact adjudication,
   then cross-system-heavy records, then standard records. This queue planning
   artifact does not relax the requirement to manually review all 100 records
   before precision, recall, F1, and manual semantic correctness are reported.

   Use `reports/stages/nasa_atmonto_gold_review_session_plan.md` to work in
   time-boxed manual review sessions. The current default target is 90 minutes;
   `session_01` covers 4 records, starts with `ATCSCC-GOLD-024` /
   `2026-05-18:136`, and remains a review queue only. It does not convert any
   suggested fact into gold until the reviewer confirms the decision fields,
   applies the reviewed draft, validates annotations, and freezes the reviewed
   gold set.

   Use `data/evaluation/nasa_atmonto/review_priority_packets/index.md` to work
   through those priority lanes without switching between the workload table,
   batch files, and decision templates. The packets expose copyable S0 IDs for
   `valid_candidate_fact_ids` and schema-valid S1-S3 IDs for
   `valid_cross_system_fact_ids`.

   Decision templates also include `suggested_valid_candidate_fact_ids`, which
   lists S0 facts that passed structural validation. These are copy aids only;
   they become gold only after source review and explicit copy into
   `valid_candidate_fact_ids`.

   Rejected-fact entries in `data/evaluation/nasa_atmonto/review_decisions/`
   also include `suggested_*` fields from
   `reports/stages/nasa_atmonto_rejection_adjudication.md`. These fields carry
   the finalized property-level classification, but they are not accepted gold
   decisions until a reviewer copies or edits them into `decision`, `rationale`,
   and `recommended_action`.

```bash
uv run python scripts/prepare_nasa_atmonto_gold_review_decision_progress.py
```

The decision-progress command audits the editable `review_decisions/*.jsonl`
files before applying them. It reports which records are `ready_to_apply`,
`in_progress`, `not_started`, or `needs_revision`, and it treats `suggested_*`
and `suggested_valid_candidate_fact_ids` fields as incomplete until a reviewer
confirms them in the actual decision fields.

```bash
uv run python scripts/apply_nasa_atmonto_gold_review_decisions.py
```

The apply command writes
`data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.reviewed_draft.jsonl`
by default. Replace the live gold template only after the draft validates and
the review boundary has been checked.

8. Validate the gold annotations.

```bash
uv run python scripts/validate_nasa_atmonto_gold_annotations.py
```

9. Freeze the completed gold set before running model comparisons. The freeze
   command refuses to write reviewed gold while validation is still pending.

```bash
uv run python scripts/freeze_nasa_atmonto_gold_set.py
```

Expected reviewed output:
`data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`

10. Re-run the formal experiment scorer to compute metrics against the reviewed
   gold set and available system prediction files.

```bash
uv run python scripts/run_nasa_atmonto_formal_experiment.py --skip-prepare-inputs
```

The scorer treats `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
as the formal gold source. If that frozen reviewed file is missing or fails
validation, semantic metrics remain blocked even if the live annotation template
contains partial labels.

The scoring report also emits a claim/hypothesis status table and completion
audit. Any pending audit requirement means the artifact must still be reported
as pilot/prepared-state evidence, not as a completed formal experiment.

11. Produce:

- system-level metric table;
- property-level metric table;
- rejection/error taxonomy;
- examples of true positives, false positives, false negatives, and repairs;
- claim status table for C1-C4 and H1-H4.

## Reporting Rules

- Report the current loop as a pilot / feasibility study until manual gold
  evaluation is complete.
- Keep NASA ATMONTO as schema constraint, not experiment ground truth.
- Keep accepted validator facts as structurally accepted, not semantically true.
- Report schema and semantic metrics separately.
- Report precision/recall/F1 only against completed manual gold labels.
- Do not claim operational readiness or aviation safety certification.
- Do not claim GraphRAG or ontology constraints improve Recall@k unless the
  formal metrics support that exact claim.

## Completion Gate For The Formal Study

The formal experiment is complete only when all of these are true:

- 100 sampled advisories have reviewed gold annotations.
- All four systems S0-S3 have run on the identical sample.
- JSON adherence, schema violation rate, triple precision/recall/F1, repair
  success for S3, structural acceptance for all systems, and manual semantic
  correctness are reported.
- The 288 pilot rejections have reviewed property-level decisions.
- Claims C1-C4 and hypotheses H1-H4 have explicit supported, falsified, or
  inconclusive status.
- All artifacts needed to reproduce the study are committed or explicitly listed
  as external/manual inputs.
