# NASA ATMONTO ATCSCC Formal Experiment Protocol

## Material Passport

- Artifact: formal experiment protocol for the NASA ATMONTO ATCSCC KG extraction study.
- Status: protocol draft with gold-sample template and rejection triage artifacts prepared.
- Prior stage: pilot / feasibility study.
- Pilot evidence:
  - `reports/stages/nasa_atmonto_minimal_loop_validation.md`
  - `data/ontology/curated/nasa_atmonto_schema_catalog.json`
  - `data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json`
  - `data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl`
- Formal-study inputs prepared:
  - `data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json`
  - `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
  - `docs/nasa_atmonto_gold_annotation_guide.md`
  - `data/experiments/nasa_atmonto/formal/input_records.jsonl`
  - `data/experiments/nasa_atmonto/formal/system_specs.json`
  - `data/experiments/nasa_atmonto/formal/s0_rule_only_predictions.jsonl`
  - `data/experiments/nasa_atmonto/formal/s1_llm_only_prompt_batch.jsonl`
  - `data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_prompt_batch.jsonl`
  - `data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_prompt_batch.jsonl`
  - `reports/stages/nasa_atmonto_rejection_error_analysis.md`
  - `reports/stages/nasa_atmonto_gold_annotation_validation.md`
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
- Current status: not yet tested.

### C3: Validator/Repair Benefit

Adding the validator/repair loop should improve structurally valid yield without
reducing manual semantic correctness below the LLM + schema-slice condition.

- Evidence required: repair success rate, post-repair schema violation rate, and
  manual semantic correctness on the same gold sample.
- Current status: not yet tested.

### C4: Rejection Analysis Utility

Property-level rejection analysis should separate extractor bugs from NASA
ATMONTO runtime-profile gaps.

- Evidence required: every rejection group has a reviewed action label
  (`extractor_bug`, `profile_gap`, `source_ambiguity`, or `manual_review_only`)
  and a regression or profile-extension follow-up.
- Current status: initial triage exists; final adjudication is pending manual review.

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
- Falsified if S3 structural repair success rate is below 15 percent of initially
  invalid S2 facts, or if S3 manual semantic correctness is more than 5
  percentage points lower than S2.

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

Current sample properties:

- Sample size: 100 advisories.
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

The gold set is complete only after manual annotation and adjudication. The
current JSONL is an annotation template, not completed gold truth.

## Systems Under Test

Prepared execution files:

- Common input records: `data/experiments/nasa_atmonto/formal/input_records.jsonl`
- System specs: `data/experiments/nasa_atmonto/formal/system_specs.json`
- S0 baseline predictions: `data/experiments/nasa_atmonto/formal/s0_rule_only_predictions.jsonl`
- S1 prompt batch: `data/experiments/nasa_atmonto/formal/s1_llm_only_prompt_batch.jsonl`
- S2 prompt batch: `data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_prompt_batch.jsonl`
- S3 prompt batch: `data/experiments/nasa_atmonto/formal/s3_llm_schema_slice_validator_repair_prompt_batch.jsonl`
- Pending/scoring report: `reports/stages/nasa_atmonto_formal_experiment_scoring.md`

These files prepare model inputs and the deterministic baseline only. They do
not contain fabricated LLM results.

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

### Triple Precision, Recall, And F1

Manual gold facts define the denominator. A predicted fact matches a gold fact
only when normalized subject class, predicate, object/value, datatype, and
source evidence are compatible under the annotation guide.

Formulas:

```text
precision = true_positive_facts / predicted_facts
recall = true_positive_facts / gold_facts
f1 = 2 * precision * recall / (precision + recall)
```

Report micro-averaged scores and property-level scores. Do not hide
property-level failures inside a single average.

### Repair Success Rate

Report both structural and semantic repair success.

```text
structural_repair_success = repaired_accepted_facts / initially_invalid_facts
semantic_repair_success = repaired_true_positive_facts / repaired_accepted_facts
```

Structural success alone is not evidence of semantic correctness.

### Manual Semantic Correctness

Percentage of structurally accepted facts judged correct by manual review.

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

Initial interpretation:

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

4. Complete manual annotation in
   `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`.

5. Validate the gold annotations.

```bash
uv run python scripts/validate_nasa_atmonto_gold_annotations.py
```

6. Freeze the completed gold set under a new filename before running model
   comparisons, for example:

```text
data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl
```

7. Run S1, S2, and S3 from the prepared prompt batches on the same 100 source
   records. Use the committed S0 prediction file as the deterministic baseline.

8. Re-run the formal experiment scorer to compute metrics against the reviewed
   gold set and available system prediction files.

```bash
uv run python scripts/run_nasa_atmonto_formal_experiment.py --skip-prepare-inputs
```

9. Produce:

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
  success, and manual semantic correctness are reported.
- The 288 pilot rejections have reviewed property-level decisions.
- Claims C1-C4 and hypotheses H1-H4 have explicit supported, falsified, or
  inconclusive status.
- All artifacts needed to reproduce the study are committed or explicitly listed
  as external/manual inputs.
