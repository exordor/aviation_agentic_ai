# NASA ATMONTO ATCSCC Formal Experiment Protocol

## Material Passport

- Artifact: formal experiment protocol for the NASA ATMONTO ATCSCC KG extraction
  study and source-family remediation.
- Status: protocol, reviewed 100-record gold set, S0-S3 prediction outputs,
  S1b/S4 corrected-stage derived outputs, rejection triage, and formal scoring
  artifacts prepared.
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
- Claim boundary: retrospective extraction and validation research only. This
  protocol does not support live aviation operations, operational advisories,
  flight planning, dispatch, ATC decisions, or safety certification.

## Current Pilot Positioning

The current NASA ATMONTO ATCSCC loop is a pilot / feasibility study. It proves
that the local NASA OWL/XML files can be converted into a runtime schema
catalog, that an ATCSCC-focused schema slice can constrain extraction, and that a
custom validator can accept, reject, and repair candidate facts.

The pilot processed 718 ATCSCC advisory records from the aligned retrospective
window, produced 4429 candidate facts, accepted 4141 facts after structural
repair, and rejected 288 facts. The accepted facts remain
`bronze_until_reviewed`; structural validation is not semantic correctness.

The next experiment must therefore answer a stronger but still narrow question:

> Can a NASA ATMONTO-derived ATCSCC schema slice improve structural validity,
> evidence grounding, and selected semantic extraction quality for retrospective
> FAA ATCSCC advisory KG extraction?

This is not a general aviation KG claim. NASA ATMONTO is used as an external
TBox, schema slice, validator profile, and terminology reference; it is not
treated as the gold-truth extracted KG.

## Source Families

The corrected experiment separates two source families. Their metrics may be
compared for structural conformance, evidence grounding, and canonicalization
yield, but their semantic F1 tables must remain task-specific.

| Source family | Data shape | Extraction task | Primary design |
| --- | --- | --- | --- |
| `faa_atcscc_advisories` | Semi-structured short FAA ATCSCC advisories. | TMI/event ABox extraction. | S0 deterministic backbone plus S3 semantic enrichment and validator gate. |
| `faa_nasa_pdf_reference_documents` | Long-form PDF reference text with definitions, procedures, tables, and section hierarchy. | Terminology, definition, procedure, and source-mapping evidence extraction. | Section-aware PDF chunking plus constrained extraction; no event-instance predicates. |

Source family A is the current scored corpus. The previous run used 100 reviewed
FAA ATCSCC advisories sampled from `2026-05-14` through `2026-05-20`, with
candidate classes `GroundDelayProgramTMI`, `GroundStopTMI`, `ReRouteTMI`, and
`TrafficManagementInitiative`.

Source family B is a planned second source-family pilot. It should use the
already-downloaded FAA/NASA reference PDFs, especially:

- `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf`
- `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf`
- optional ontology documentation evidence:
  `data/papers/ntrs_ontology_selection/20170006095_nasa_air_traffic_management_ontology.pdf`

PDF extraction must target reference-text predicates such as
`term_has_definition`, `term_has_alias`, `procedure_mentions_concept`,
`document_defines_or_constrains`, and `source_supports_mapping`. Each extracted
PDF fact must include `document_id`, `page`, `section`, `span`, and
`evidence_text`. Do not mix these PDF definition/procedure facts with ATCSCC
event-instance predicates such as `advisoryNumber`, `effectiveStartTime`, or
`controlledNASelement` in the same semantic F1 table.

The PDF backend policy follows the existing project reports:
`hybrid_docling_pymupdf` is the candidate default, while
`pymupdf_text_legacy` is a baseline only. The policy is grounded in
`reports/stages/pdf_extraction_comparison.md` and
`reports/stages/pdf_backend_chunking_comparison.md`.

## Consensus SOTA Adaptation For The Rerun

The rerun uses the Consensus and ChatGPT Pro methodology reviews as design
constraints for this narrow ATCSCC / ATMONTO study. They do not change the
project into a general aviation KG or a broad GraphRAG benchmark.

The current all-zero `S1_llm_only` result is treated as an ontology-interface
and canonicalization failure. `S1_raw_open_llm` is a drift diagnostic and must
not report target-schema precision, recall, or F1. `S1b_llm_canonicalized`
maps open facts into the ATMONTO profile and is the comparable baseline for
S2/S3/S4.

The next rerun should follow a nine-stage pipeline:

1. ATCSCC parsing.
2. S0 deterministic backbone.
3. Schema-slice retrieval.
4. LLM semantic extraction.
5. Canonicalization.
6. Validator gate.
7. Repair with trace.
8. Graph materialization.
9. Layered evaluation.

The Extract-Define-Canonicalize design separates open extraction from
target-schema scoring. Ontology-guided short-text KGC motivates 10-20
`reviewed_dev_examples` for S2/S3, selected by advisory type and predicate
family. These examples must come from a development split outside the
held-out 100 scoring records.

LLMs are used as canonicalizers, semantic enrichment modules, evidence checkers,
and profile-gap explainers. They are not the primary thesis system by
themselves. The primary candidate for the next ATCSCC extraction rerun is
`S4_hybrid_backbone_enrichment`: pattern/rule extraction plus ontology-guided
prompting, grounding, corroboration, validator gating, and review quarantine.

S4 merge rules:

- S0 wins for `advisoryNumber`, `issuedTime`, `effectiveStartTime`,
  `effectiveEndTime`, and other header/template fields.
- S3/S4 may add, but not overwrite, semantic facts such as `reRouteReason`,
  `reRouteType`, and `implementationStatus`.
- Conflicts, unsupported spans, fuzzy-only mappings, validator-rejected facts,
  and repair-only facts with semantic-change flags go to log/review/quarantine.

Planned implementation artifacts:

- `schema/atcscc_tmi_profile.yaml` with `class`, `predicate_uri`, `label`,
  `aliases`, `domain`, `range`, `cardinality`, `allowed_enum`, `normalizer`,
  `validator_rule`, `example_spans`, `profile_version`, `source_doc`, and
  `commit_hash`.
- Predicate canonicalizer, enum canonicalizer, entity canonicalizer, and time
  normalizer.
- Repair trace with pre-error, repair action, post-validation status,
  semantic-change flag, evidence status, and repair-induced false positive
  accounting.
- Error taxonomy: format error, predicate drift, class/domain error, range
  error, enum error, entity canonicalization error, unsupported span, temporal
  normalization error, and duplicate/merge error.

GraphRAG evaluation remains layered. KG construction, graph retrieval, answer
faithfulness/completeness, and citation support must be reported separately.
The current remediation only supports KG construction metrics; it must not be
used to claim end-to-end GraphRAG answer improvement.

Additional Pro-review leads such as OntoLogX, JSON-Schema-guided information extraction,
Graphusion, RAKG, RAGAS, STaRK, and Microsoft GraphRAG are
`requiring verification`. They are search leads only until directly fetched and
checked.

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
domain/range violations than a schema-free extractor after the schema-free
output has a documented canonicalization bridge.

- Evidence required: lower schema violation rate for `LLM + schema slice` than
  `S1b_llm_canonicalized` on the same gold-sampled records.
- Current status: inconclusive for semantic baseline comparison. The saved
  `S1_llm_only` run is JSON-adherent but all 1211 facts are rejected by direct
  ATMONTO target-schema scoring, so its P/R/F1 are
  `invalid_direct_schema_scoring` diagnostics rather than a valid LLM-only
  semantic baseline.

### C3: Validator/Repair Benefit

Adding the validator/repair loop should improve structurally valid yield without
reducing manual semantic correctness below the LLM + schema-slice condition.

- Evidence required: repair success rate, post-repair schema violation rate, and
  manual semantic correctness on the same gold sample.
- Current status: supported on the reviewed 100-record sample: S3 improves
  structural acceptance versus S2 and does not reduce manual semantic
  correctness in the frozen-gold scoring report. This is not evidence that S3
  beats an unconstrained LLM semantic baseline until `S1b_llm_canonicalized` is
  added.

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

### C5: Source-Family Separation

ATCSCC advisories and PDF reference documents should be evaluated as separate
source families with task-specific semantic metrics.

- Evidence required: protocol and reports separate ATCSCC event ABox extraction
  from PDF definition/procedure/reference extraction; shared metrics are limited
  to structural conformance, evidence grounding, and canonicalization yield.
- Current status: remediation requirement. The current scored run covers only
  ATCSCC advisories; PDF source-family B is a planned second pilot using PCG,
  JO 7110.65BB, and optional NASA ATMONTO documentation passages.

## Hypotheses And Falsification Criteria

### H1: Schema Guidance Reduces Structural Drift After Canonicalization

Compared with `S1b_llm_canonicalized`, `LLM + schema slice` will reduce
unsupported target-schema terms and schema violation rate.

- Primary comparison: S2 vs S1b.
- Falsified if S2 schema violation rate is not lower than S1b by at least 10
  percentage points, or if bootstrap confidence intervals show no practical
  separation.
- Secondary failure mode: S2 achieves lower violations only by suppressing more
  than 25 percent of gold-supported facts relative to S1b.
- Current interpretation: supported on the corrected stage. S1 direct schema
  scoring remains an interface-failure diagnostic, while
  `S1b_llm_canonicalized` provides the comparable canonicalized baseline.

### H2: Validator/Repair Improves Valid Yield

Compared with `LLM + schema slice`, `LLM + schema slice + validator/repair` will
increase structurally accepted facts while preserving manual semantic correctness.

- Primary comparison: S3 vs S2.
- Falsified if S3 structural repair success rate is below 15 percent of facts
  that enter the S3 validator/repair loop as initially invalid, or if S3 manual
  semantic correctness is more than 5 percentage points lower than S2.

### H3: Hybrid Backbone Plus Enrichment Improves Selected Semantic Predicates

The next candidate system should combine the deterministic ATCSCC parser with
schema-constrained LLM enrichment.

- Primary comparison: S4 vs S0 for selected semantic predicates where S0 is
  weak, especially `reRouteReason`, `reRouteType`, and
  `implementationStatus`.
- Preservation criterion: S4 must preserve S0 F1 for deterministic fields such
  as `advisoryNumber`, `issuedTime`, `effectiveStartTime`, and
  `effectiveEndTime` within a pre-registered tolerance.
- Falsified if S4 does not improve the selected semantic predicate family or if
  it materially harms deterministic-field F1.
- Current interpretation: supported on the corrected stage for the selected
  semantic predicate family. This is not an aggregate end-to-end GraphRAG or
  general aviation KG claim.

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

The current scored ATCSCC run uses the original four saved systems plus two
corrected-stage derived systems on the identical 100-record advisory sample.
S1 direct target-schema scoring remains a diagnostic artifact because a
schema-free output was scored without canonicalization; S1b and S4 are the
corrected comparators.

| System | Role | Comparator Question |
| --- | --- | --- |
| S0 rule-only | Deterministic parser baseline | How much can a low-cost rule extractor recover before LLMs? |
| S1 LLM-only | Historical direct-scoring diagnostic | How much target-schema interface failure appears without ontology terms or canonicalization? |
| S2 LLM + schema slice | Schema-guided extraction condition | Does a compact ATCSCC slice reduce unsupported terms? |
| S3 LLM + schema slice + validator/repair | Full ontology-constrained loop | Does validation/repair improve accepted yield without semantic loss? |

The corrected next-rerun suite should add:

| System | Role | Scoring boundary |
| --- | --- | --- |
| `S1_raw_open_llm` | Schema-free open extraction with generic entities, events, attributes, relations, times, evidence spans, and confidence. | Raw JSON, evidence, coverage, and drift diagnostics only; no direct ATMONTO P/R/F1. |
| `S1b_llm_canonicalized` | Post-hoc canonicalization bridge from S1 raw output into the ATMONTO fact schema. | Target-schema P/R/F1 after canonicalization. Implemented as a deterministic corrected-stage derivation from saved S1 facts. |
| `S4_hybrid_backbone_enrichment` | S0 deterministic backbone plus S3 semantic enrichment and validator gate. | Primary candidate system for ATCSCC event extraction. Implemented as a deterministic corrected-stage merge from saved S0 and S3 facts. |

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

- Purpose: historical measure of direct schema-interface drift.
- Constraint: no ontology term list in the prompt.
- Validator role: post-hoc measurement only; no repair loop.
- Current interpretation: `invalid_direct_schema_scoring` for semantic
  P/R/F1. The saved S1 run produced JSON, but all 1211 facts were rejected by
  the target ATMONTO validator. This is evidence that an open baseline needs
  `S1_raw_open_llm` plus `S1b_llm_canonicalized`, not evidence that the LLM
  extracted no useful information.

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

### S4: Hybrid Backbone + Semantic Enrichment

S4 is the recommended next ATCSCC system rather than a replacement for S0. It
should merge S0 and S3 with predicate-family rules:

- Preserve S0 facts for semi-structured deterministic fields:
  `advisoryNumber`, `issuedTime`, `effectiveStartTime`, and
  `effectiveEndTime`.
- Use S3 as semantic enrichment for predicates where S0 is weak, especially
  `reRouteReason`, `reRouteType`, `implementationStatus`, and evidence-rich
  comments.
- Quarantine conflicts, unsupported spans, fuzzy-only mappings, and repair-only
  facts with semantic-change flags for review.
- Validate the final merged output with the ATMONTO schema-slice validator.

### PDF Reference Extraction Systems

PDF source-family B should not reuse the ATCSCC event systems unchanged. Its
default backend is `hybrid_docling_pymupdf`; `pymupdf_text_legacy` remains a
baseline. The PDF extraction task should use page/section/span provenance and
target reference predicates only:

- `term_has_definition`
- `term_has_alias`
- `procedure_mentions_concept`
- `document_defines_or_constrains`
- `source_supports_mapping`

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

For PDF source-family B, semantic scores must be reported in a separate
definition/procedure/reference table. Do not compare PDF
`term_has_definition` F1 directly against ATCSCC `advisoryNumber` or
`effectiveStartTime` F1. Cross-source comparison is limited to JSON adherence,
schema conformance, evidence-span validity, and canonicalization yield.

### Canonicalization Yield

For schema-free extraction baselines, report canonicalization yield before
target-schema semantic scores:

```text
canonicalization_yield = canonicalized_target_schema_facts / raw_open_facts
```

`S1_raw_open_llm` has no direct target-schema semantic F1. Only
`S1b_llm_canonicalized` can enter target-schema precision/recall/F1.

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
   S1b/S4 derived predictions when their source outputs exist, readiness
   report, and the scoring report.

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

5. Validate S1/S1b/S2/S3/S4 prediction JSONL files and run metadata before
   scoring.

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

For the remediation rerun, replace the direct S1 semantic comparison with:

```bash
# planned names; implementation may split generation and canonicalization
uv run python scripts/run_nasa_atmonto_llm_predictions.py S1_raw_open_llm --resume
uv run python scripts/canonicalize_nasa_atmonto_open_llm.py S1_raw_open_llm
```

The raw S1 output should contain generic entities, events, attributes,
relations, quantities/times, evidence spans, and confidence. The canonicalizer
creates `S1b_llm_canonicalized`; only S1b enters ATMONTO target-schema
precision/recall/F1.

For PDF source-family B, create a separate passage-level input set and do not
append PDF passages to the ATCSCC advisory input JSONL. The PDF pilot should use
PCG and JO 7110.65BB first, optionally adding NASA ATMONTO technical
documentation for ontology term-boundary evidence. Each PDF fact must carry
`document_id`, `page`, `section`, `span`, and `evidence_text`.

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
- Do not claim end-to-end GraphRAG answer improvement from KG construction
  metrics alone; retrieval and answer-generation layers need separate evidence.

## Completion Gate For The Formal Study

The formal experiment is complete only when all of these are true:

- 100 sampled advisories have reviewed gold annotations.
- S0, diagnostic S1, S1b, S2, S3, and S4 have run on the identical sample.
- JSON adherence, schema violation rate, triple precision/recall/F1, repair
  success for S3, structural acceptance for all systems, and manual semantic
  correctness are reported.
- The 288 pilot rejections have reviewed property-level decisions.
- Claims C1-C4 and hypotheses H1-H4 have explicit supported, falsified, or
  inconclusive status.
- All artifacts needed to reproduce the study are committed or explicitly listed
  as external/manual inputs.
