# Cross-source Thesis Mainline Closure Plan

> Completed on 2026-07-13. The generated evidence is
> `reports/stages/cross_source_mainline_evaluation.{json,md}`; full verification
> passed with Ruff and 380 tests.

## Decision

The cross-source V2 subsystem is promoted from an additive future-work track to
the thesis mainline. The thesis remains retrospective and source-bounded. It
does not claim live ATC decision support, causal attribution from temporal
co-occurrence, a complete aviation ontology, or expert-certified autonomy.

Neo4j is an inspectability and demonstration surface. The research object is
the authority-grounded, evidence-layered, autonomously gated cross-source
KG-RAG method.

## Revised Mainline

```text
ATCSCC advisories + FAA terminology + NASR facilities + METAR/TAF
  -> versioned source snapshots
  -> schema-constrained advisory extraction
  -> canonical facility and terminology alignment
  -> autonomous context alignment and quarantine
  -> canonical/audit knowledge graphs
  -> facility/time cross-source associations
  -> text-only and graph-enabled answer baselines
  -> evidence-layered answers, citations, abstention, and failure analysis
```

## Canonical Research Questions

1. Can schema-constrained extraction and canonicalization produce valid,
   evidence-linked ATCSCC event records?
2. Can agentic validation and autonomous context alignment reduce unsupported
   facts and resolve or quarantine ambiguous aviation abbreviations?
3. Does authority-grounded cross-source KG-RAG improve evidence coverage,
   citation support, and unsupported-claim control over matched source-only and
   linked-text baselines?
4. Which extraction, alignment, linking, retrieval, answer, and abstention
   failures remain, and how reliably can the runtime quarantine them without
   human intervention?

## Evaluation Layers

| Layer | Primary evidence | Main metrics |
| --- | --- | --- |
| Advisory extraction | Frozen reviewed 100-record ATCSCC set | P/R/F1, schema violations, evidence support |
| Facility/term alignment | All 718 advisories plus hard ambiguity challenge set | target accuracy, accept/quarantine accuracy, coverage |
| Cross-source linking | Frozen 68-record JFK/EWR/LGA cohort | facility coverage, temporal-rule validity, link provenance |
| Cross-source QA | 24-case evaluation set | evidence-layer coverage, citation support, abstention, causal-overstatement failures |
| Baseline comparison | Same sources/questions/snapshot set | source-only vs linked-text vs KG-layered deltas |

Automated runtime and scientific evaluation are separate. The production path
must not require human review. Scientific correctness claims require an
independent expected-output artifact or reviewed subset; a policy regression
alone supports only implementation conformance.

## Implementation Sequence And Gates

1. **Governance integration**
   - Update `RESEARCH_OVERVIEW.md`, `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`,
     `RESULTS.md`, `EXPERIMENTS.md`, and `TODO.md`.
   - Gate: cross-source work is no longer described as non-thesis future work.
2. **Hard ambiguity evaluation**
   - Add explicit Ground Stop, Glide Slope, neutral, and conflicting `GS`
     contexts with expected accepted/quarantined outcomes.
   - Gate: both successful resolution and fail-closed behavior are measured.
3. **Matched cross-source baselines**
   - Evaluate source-only, linked-text, and KG-layered modes on identical
     questions and pinned inputs.
   - Gate: metrics remain layer-specific; no mixed overall score.
4. **Independent evaluation report**
   - Generate machine-readable and Markdown results with failure cases.
   - Gate: distinguish policy conformance from semantic correctness.
5. **Thesis synthesis**
   - Add cross-source methods/results; rewrite Discussion, Threats/Limitations,
     and Conclusion.
   - Gate: every quantitative claim points to a tracked artifact.
6. **Delivery boundary**
   - Preserve unrelated user artifacts, run full verification, and propose
     reviewable commits without silently committing.

## Completion Definition

The closure is complete when the canonical research documents agree on the
cross-source mainline, the ambiguity and baseline evaluations run from pinned
artifacts, the thesis report incorporates their bounded results, and repository
tests plus formatting checks pass.
