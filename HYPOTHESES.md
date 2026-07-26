# Research Hypotheses

> **Optional historical evaluation framing.** These hypotheses are retained for
> reproducibility and possible future evaluation. They are not current system
> requirements, and their prior status labels must not be read as proof of the
> present multi-Agent system's overall quality.
>
> Revised on 2026-07-13. Hypotheses use descriptive names rather than internal
> numeric codes. Machine artifact names remain unchanged for reproducibility.

## Summary

| Hypothesis | Primary comparison or evidence | Status |
| --- | --- | --- |
| Schema guidance reduces structural drift after canonicalization | Canonicalized schema-free extraction versus schema-guided extraction | supported on the corrected stage |
| Validator and repair improve structurally valid yield | Schema-guided extraction before and after validator/repair | supported on the reviewed 100-record sample |
| Routed KG-RAG improves source-bounded grounding | Vector, graph, hybrid, and routed retrieval over the 317-case benchmark | partially supported: routing helps relation-oriented questions; unconditional graph use hurts abstention |
| Failure analysis separates actionable error categories | Rejection reports, alignment quarantine, answer critic, and independent audit | supported on the current taxonomy |
| Deterministic backbone plus semantic enrichment improves selected predicates | Hybrid extraction versus the deterministic baseline | supported for the selected semantic predicate family |
| Rejection triage produces actionable engineering decisions | Property-level rejection analysis | supported |
| Authority-grounded context alignment resolves or quarantines ambiguity | Twenty Ground Stop, Glide Slope, neutral, and conflicting cases | supported: target and quarantine accuracy 1.00, zero out-of-registry acceptances |
| KG-layered cross-source answers improve evidence coverage | Twenty-four matched source-only, linked-text, and KG-layered questions | supported: layer/citation coverage 1.00 versus 0.75 and 0.25, with zero causal overstatements |

Status vocabulary: `pending`, `supported`, `rejected`, `partially_supported`,
`inconclusive`, `abandoned`, `needs_replication`.

## Schema Guidance Reduces Structural Drift

Compared with schema-free extraction after canonicalization, schema-guided
extraction should reduce unsupported target-schema terms and schema violations.

- Primary comparison: canonicalized schema-free extraction versus
  schema-guided extraction.
- Falsified if schema-guided extraction does not reduce the violation rate by at
  least ten percentage points, or bootstrap confidence intervals show no
  practical separation.
- Secondary failure mode: lower violations are achieved only by suppressing
  more than 25 percent of gold-supported facts.
- Current interpretation: supported on the corrected stage. Directly scoring
  raw schema-free output remains an interface-failure diagnostic rather than a
  fair semantic comparison.

## Validator And Repair Improve Valid Yield

Adding the validator and repair loop should increase structurally accepted
facts while preserving reviewed semantic correctness.

- Primary comparison: schema-guided extraction before and after
  validator/repair.
- Falsified if repair succeeds on fewer than 15 percent of initially invalid
  facts, or reviewed semantic correctness falls by more than five percentage
  points.

## Routed KG-RAG Improves Source-Bounded Grounding

Graph-aware retrieval should improve relation-oriented answers, evidence
grounding, and citation behavior, while vector retrieval may remain sufficient
for source-local questions.

- Primary comparison: graph-only, hybrid, routed graph, and vector-only modes
  over the same 317 cases.
- Falsified if graph-aware modes improve no retrieval or answer-grounding
  diagnostic, or gains occur only in undeployable source-oracle conditions.
- Current interpretation: partially supported. Routed graph use reaches answer
  F1 around 0.98 and abstention correctness 1.00; unconditional graph and hybrid
  use degrade answer quality and abstention.

## Failure Analysis Separates Actionable Categories

Residual failures should be assignable to extraction, alignment, linking,
retrieval context, answer overreach, or evaluation-boundary categories.

- Falsified if a substantial share of failures cannot be assigned or the
  runtime silently accepts low-information conflicts.
- Current interpretation: supported on the current taxonomy. The independent
  Evaluation Agent passes 24/24 cross-source audits; external expert
  certification remains outside the claim.

## Deterministic Backbone Plus Enrichment Improves Selected Predicates

The candidate extraction system combines deterministic parsing with
schema-constrained semantic enrichment.

- Primary comparison: hybrid extraction versus the deterministic baseline for
  reroute reason, reroute type, and implementation status.
- Preservation criterion: hybrid extraction must preserve performance on
  advisory number and effective-time fields within the registered tolerance.
- Falsified if semantic predicates do not improve or deterministic fields are
  materially harmed.

## Rejection Triage Produces Actionable Engineering Decisions

Most rejected facts should be classifiable into a small set of property-level
causes.

- Falsified if more than 20 percent remain unresolved after deterministic
  adjudication, or a proposed profile extension lacks source evidence and a
  corresponding ontology term.

## Authority-Grounded Alignment Resolves Or Quarantines Ambiguity

For registry-supplied `GS` candidates, traffic-management cues should resolve
to Ground Stop, instrument-approach cues should resolve to Glide Slope, and
neutral or conflicting contexts should be quarantined.

- Falsified if accepted-target accuracy or quarantine accuracy is below 0.95,
  or any out-of-registry target enters the canonical graph.
- Current interpretation: supported on the twenty-case challenge: 14/14
  accepted targets, 6/6 quarantines, and zero out-of-registry acceptances.
- Claim boundary: this covers one documented abbreviation family rather than
  universal acronym disambiguation.

## KG-Layered Cross-Source Answers Improve Evidence Coverage

On identical questions and pinned source records, KG-layered answers should
cover more required evidence and citation layers than source-only and
linked-text answers while preserving the non-causal association boundary.

- Primary metrics: evidence-layer coverage, citation-layer coverage,
  abstention accuracy, alignment-explanation accuracy, and Evidence Critic
  failures.
- Falsified if KG-layered answers do not improve both coverage measures over
  both baselines, or introduce any causal-overstatement failure.
- Current interpretation: supported on 24 matched questions. Evidence and
  citation coverage is 0.25 for source-only, 0.75 for linked text, and 1.00 for
  KG-layered answers; causal-overstatement count is zero.
- Claim boundary: this is a deterministic component ablation, not a broad LLM
  or GraphRAG benchmark.
