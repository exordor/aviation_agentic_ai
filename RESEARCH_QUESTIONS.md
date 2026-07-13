# Research Questions

> Revised on 2026-07-13. Questions and hypotheses use descriptive names rather
> than internal numeric codes.

## Schema-Constrained Extraction And Canonicalization

### Question

Can schema-constrained extraction and canonicalization produce valid,
evidence-linked event records from retrospective ATCSCC advisories?

### Why It Matters

ATCSCC notices combine reliable template fields with semantic operational
fields. The experiment tests whether deterministic parsing, a lightweight
ATMONTO-derived profile, and constrained enrichment preserve supported facts
while preventing schema drift.

### Related Hypotheses

- Schema guidance reduces structural drift after canonicalization.
- Deterministic backbone plus semantic enrichment improves selected predicates.

### Evidence

- Six extraction conditions over the frozen 100-record reviewed sample:
  deterministic rules, raw schema-free LLM extraction, canonicalized LLM
  extraction, schema-guided extraction, validator/repair, and hybrid enrichment.
- `reports/stages/nasa_atmonto_formal_experiment_scoring.md`.
- `reports/stages/nasa_atmonto_prediction_output_validation.md`.

### Current Answer

Supported on the current source-bounded experiment. Deterministic parsing is
strongest for template fields; hybrid extraction improves selected semantic
predicates while retaining evidence and schema gates.

## Agentic Validation And Autonomous Ambiguity Alignment

### Question

Can agentic validation and autonomous context alignment reduce unsupported
facts and either resolve or quarantine ambiguous aviation abbreviations before
they enter the canonical graph?

### Why It Matters

Facility identifiers and ATCSCC contractions are prerequisites for cross-source
links. A manual adjudication dependency does not meet the system goal, while
unrestricted LLM alignment can silently corrupt the graph. The method combines
authority registries, contextual ranking, critic thresholds, and fail-closed
quarantine.

### Related Hypotheses

- Validator and repair improve structurally valid yield.
- Authority-grounded context alignment resolves discriminating cases and
  quarantines neutral or conflicting ambiguity.

### Evidence

- Validator, refiner, and critic diagnostics over the reviewed extraction set.
- Facility and terminology alignment over all 718 advisories.
- Twenty Ground Stop, Glide Slope, neutral, and conflicting `GS` cases.
- `docs/cross_source_multi_agent_v2_design.md`.

### Current Answer

Supported on the current experiments. The pinned advisory run accepts 8,403
mappings, including 68 contextual `GS` decisions. The hard challenge achieves
1.00 accepted-target accuracy, 1.00 quarantine accuracy, and zero
out-of-registry acceptances. This covers one ambiguity family rather than
universal acronym disambiguation.

## Cross-Source KG-RAG Grounding

### Question

Does authority-grounded cross-source KG-RAG improve evidence coverage,
citation support, and unsupported-claim control over matched source-only and
linked-text baselines?

### Why It Matters

The graph is useful only if canonical facility and term identity plus explicit
evidence layers improve relation-oriented answers. Facility/time association
must remain separate from source-declared causality. Simple source-local
questions may still be better served without graph traversal.

### Related Hypotheses

- Routed KG-RAG improves source-bounded grounding on relation-oriented
  questions while vector retrieval remains sufficient for simpler questions.
- KG-layered cross-source answers improve required evidence and citation
  coverage over matched source-only and linked-text baselines.

### Evidence

- A 317-case single-source retrieval benchmark and a 30-question vector-only
  versus routed KG-RAG answer comparison.
- The frozen 68-record JFK/EWR/LGA cohort linked to METAR and TAF.
- Twenty-four identical cross-source questions evaluated with source-only,
  linked-text, and KG-layered answers.
- Neo4j is an inspectability surface rather than the research comparison.

### Current Answer

Supported within the matched component design. Routed graph use helps
relation-oriented questions. In the 24 cross-source cases, required evidence
and citation-layer coverage is 1.00 for KG-layered answers versus 0.75 for
linked text and 0.25 for source-only answers, with zero causal overstatements.

## Autonomous Failure And Abstention Boundary

### Question

Which extraction, alignment, linking, retrieval, answer, and abstention
failures remain, and how reliably can the runtime quarantine them without human
intervention?

### Why It Matters

Runtime autonomy and scientific validation are separate. The workflow must
accept, quarantine, reject, or abstain without a manual queue. The thesis must
still evaluate whether those decisions match independent expectations and must
report unsupported claims and causal overstatement explicitly.

### Related Hypotheses

- Failure analysis separates actionable error categories.
- Rejection triage produces actionable engineering decisions.
- Low-information or conflicting ambiguity is quarantined.

### Evidence

- Rejection adjudication and answer-failure reports.
- Cross-source alignment quarantine and Answer Evidence Critic artifacts.
- The hard ambiguity challenge and 24-case matched evaluation.

### Current Answer

Supported for the declared failure taxonomy and automated properties. The
runtime has no human-review dependency; the hard challenge reaches 1.00
quarantine accuracy, all answer modes preserve expected abstention, and the
independent Evaluation Agent passes 24/24 cross-source evidence audits.
External expert certification remains outside the claim.
