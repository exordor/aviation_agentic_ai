# Hypotheses

> Migrated on 2026-07-05 from `docs/experiment_protocol.md` §Hypotheses And Falsification Criteria and `docs/thesis_positioning.md` §Hypotheses. Until the archive commit lands, the source files remain in place under `docs/`; afterward they will be preserved under `docs/archive/governance_era/`.

## Canonical vs operational numbering

This file uses conceptual hypothesis IDs (H1–H4) as the canonical reference, drawn from the thesis positioning. The formal experiment protocol (`EXPERIMENTS.md` §Hypotheses And Falsification Criteria) carries operational hypotheses with falsification criteria; its operational H3 (S4 hybrid extraction) and H4 (rejection triage) are renumbered here as canonical H5 and H6 to avoid clashing with the conceptual H3 (KG-RAG grounding) and H4 (failure taxonomy). The mapping:

| Canonical (this file) | EXPERIMENTS.md operational | Hypothesis |
|---|---|---|
| H1 | H1 | Schema guidance reduces structural drift after canonicalization. |
| H2 | H2 | Validator/repair improves valid yield. |
| H3 | (new) | KG-RAG improves source-bounded grounding, answer-set quality, and citation behavior. |
| H4 | (new) | Failure analysis separates extraction, profile/gold-boundary, retrieval, answer-overreach, and human-review cases. |
| H5 | H3 | Hybrid backbone + enrichment improves selected semantic predicates. |
| H6 | H4 | Rejection triage produces actionable engineering decisions. |

## Hypothesis Table

| ID | Hypothesis | Related RQ | Primary comparison / evidence | Status |
|---|---|---|---|---|
| H1 | Schema guidance reduces structural drift after canonicalization. | RQ1 | S2 vs S1b | supported on the corrected stage |
| H2 | Validator/repair improves valid yield. | RQ2 | S3 vs S2 | supported on the reviewed 100-record sample |
| H3 | KG-RAG improves source-bounded grounding, answer-set quality, and citation behavior on relation-oriented ATCSCC questions. | RQ3 | vector vs graph vs hybrid vs routed modes in `reports/stages/nasa_atmonto_s7_retrieval.md` | partially supported — routed/hybrid modes improve some grounding diagnostics; vector-only remains sufficient for source-local questions |
| H4 | Failure analysis separates extraction errors, profile/gold-boundary gaps, retrieval context errors, answer overreach, and human-review cases. | RQ4 | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_rejection_adjudication.md`, `reports/stages/nasa_atmonto_s7_llm_failure_review.md` | supported at category level; human-answer-review and expert-certification gates still open |
| H5 | Hybrid backbone + enrichment improves selected semantic predicates. | RQ1 / RQ3 | S4 vs S0 for selected semantic predicates | supported on the corrected stage for the selected semantic predicate family |
| H6 | Rejection triage produces actionable engineering decisions. | RQ4 | rejection-error analysis coverage | supported at property level |

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

## H3: KG-RAG Improves Source-Bounded Grounding, Answer-Set Quality, And Citation Behavior

KG-RAG modes (graph-only, hybrid, routed GraphRAG) should improve source-bounded grounding, answer-set quality, and citation behavior on relation-oriented ATCSCC questions compared with vector-only retrieval, while vector-only retrieval can remain sufficient for simple source-local questions.

- Primary comparison: graph-only / hybrid / routed GraphRAG vs vector-only modes over the 317-case S7 retrieval benchmark.
- Primary evidence: `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`.
- Falsified if KG/hybrid/routed modes do not improve any retrieval or answer-grounding diagnostic (Recall@5, target-source hit rate, answer-set F1, citation precision/recall, evidence faithfulness, abstention correctness) versus vector-only on the source-bounded benchmark, or if observed gains appear only on source-oracle modes that are not deployable.
- Secondary failure mode: gains appear only when the graph has direct gold-path support and disappear under live retrieval.
- Current interpretation: partially supported. Routed GraphRAG reaches answer-set F1 ≈ 0.98 and abstention correctness = 1.0 matching the source oracle, while graph-only/hybrid modes without routing degrade answer F1 and abstention; vector-only remains a fair baseline for source-local questions.

## H4: Failure Analysis Separates Error Categories

The remaining failures can be separated into extraction errors, profile/gold-boundary gaps, retrieval context errors, answer overreach, and cases requiring human review.

- Primary evidence: `reports/stages/nasa_atmonto_reviewer_defense_audit.md` (claim-scope gates), `reports/stages/nasa_atmonto_rejection_adjudication.md` (extractor_bug vs profile_gap adjudication), `reports/stages/nasa_atmonto_s7_llm_failure_review.md` (answer-level failures).
- Falsified if a substantial fraction of failures cannot be assigned to one of these categories, or if the human-review and expert-certification gates cannot be stated as explicit open boundary conditions.
- Current interpretation: supported at category level. Categories are enumerable; the internal-diagnostic package is complete while human-answer-review and external-expert-certification remain explicitly open.

## H5: Hybrid Backbone Plus Enrichment Improves Selected Semantic Predicates

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

## H6: Rejection Triage Produces Actionable Engineering Decisions

Most rejected facts should be classifiable into a small set of actionable
property-level causes.

- Primary evidence: `reports/stages/nasa_atmonto_rejection_error_analysis.md`.
- Falsified if more than 20 percent of rejected facts remain
  `manual_review_required` after review, or if a proposed profile extension
  cannot be tied to source evidence and a NASA ATMONTO term.
