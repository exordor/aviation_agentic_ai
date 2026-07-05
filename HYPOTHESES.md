# Hypotheses

> Migrated on 2026-07-05 from `docs/experiment_protocol.md` §Hypotheses And Falsification Criteria and `docs/thesis_positioning.md` §Hypotheses. Sources preserved under `docs/archive/governance_era/`.

## Hypothesis Table

| ID | Hypothesis | Related RQ | Primary comparison | Status |
|---|---|---|---|---|
| H1 | Schema guidance reduces structural drift after canonicalization. | RQ1 | S2 vs S1b | supported on the corrected stage |
| H2 | Validator/repair improves valid yield. | RQ2 | S3 vs S2 | supported on the reviewed 100-record sample |
| H3 | Hybrid backbone + enrichment improves selected semantic predicates. | RQ1 / RQ3 | S4 vs S0 for selected semantic predicates | supported on the corrected stage for the selected semantic predicate family |
| H4 | Rejection triage produces actionable engineering decisions. | RQ4 | rejection-error analysis coverage | supported at property level |

Status vocabulary: `pending`, `supported`, `rejected`, `partially_supported`, `inconclusive`, `abandoned`, `needs_replication`.

## H1: Schema Guidance Reduces Structural Drift After Canonicalization

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

## H2: Validator/Repair Improves Valid Yield

Compared with `LLM + schema slice`, `LLM + schema slice + validator/repair` will
increase structurally accepted facts while preserving manual semantic correctness.

- Primary comparison: S3 vs S2.
- Falsified if S3 structural repair success rate is below 15 percent of facts
  that enter the S3 validator/repair loop as initially invalid, or if S3 manual
  semantic correctness is more than 5 percentage points lower than S2.

## H3: Hybrid Backbone Plus Enrichment Improves Selected Semantic Predicates

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

## H4: Rejection Triage Produces Actionable Engineering Decisions

Most rejected facts should be classifiable into a small set of actionable
property-level causes.

- Primary evidence: `reports/stages/nasa_atmonto_rejection_error_analysis.md`.
- Falsified if more than 20 percent of rejected facts remain
  `manual_review_required` after review, or if a proposed profile extension
  cannot be tied to source evidence and a NASA ATMONTO term.
