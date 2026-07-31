# Thesis Writing Spine

> **Historical writing scaffold — superseded.** The extractor/validator/
> refiner/critic narrative below describes an earlier research phase and must
> not be used as the current method section. Start from `RESEARCH_OVERVIEW.md`,
> `RESEARCH_AUDIT.md`, and `docs/multi_agent_kg_system_design.md`.

## Working Title

Evidence-Grounded Schema-Constrained Agentic KG-RAG for FAA ATCSCC Advisories

## One-Paragraph Abstract Draft

FAA ATCSCC advisories are public, semi-structured operational notices that
describe traffic management events, affected NAS elements, effective time
windows, causes, and operational constraints. This project investigates a
source-bounded method for extracting advisory-event knowledge from retrospective
ATCSCC advisories using a lightweight schema, evidence spans, and an agentic
validator/refiner/critic loop. The accepted facts are materialized as an
evidence-linked advisory event graph and evaluated in a vector, graph, and
routed KG-RAG question-answering setting. Results are reported with layered
metrics for schema validity, provenance, extraction quality, answer grounding,
citations, unsupported claims, and failure boundaries. The system is a
retrospective research prototype, not a complete aviation ontology or live ATC
decision-support system.

## Core Contribution

The project contributes a bounded, reproducible pipeline for schema-constrained
and evidence-grounded advisory-event extraction, validation, graph construction,
and KG-RAG answer evaluation over FAA ATCSCC advisories.

## Contributions

| Contribution | Evidence artifact |
|---|---|
| Lightweight ATCSCC application schema/profile | `reports/stages/atcscc_ontology_profile_overview.md` |
| Evidence-linked advisory-event extraction | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` |
| Agentic validation/refinement diagnostics | `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` |
| Source-bounded KG-RAG answer comparison | `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`, `reports/stages/nasa_atmonto_s7_vector_only_llm_answer_generation.md` |
| Failure and claim-safety boundary | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_s7_retrieval.md` |

## Method Figure Plan

Use one compact SOTA-style pipeline figure:

```text
ATCSCC advisory snapshot
  -> schema/profile gate
  -> extractor
  -> validator/refiner/critic loop
  -> evidence-linked event graph
  -> vector / graph / routed KG-RAG
  -> answer and failure evaluation
```

The figure must show that the LLM does not decide authority and that every
accepted fact is checked against schema and evidence boundaries.

## Experiment Table Plan

| research question | Systems compared | Primary metrics | Evidence |
|---|---|---|---|
| Schema-constrained extraction | deterministic rules, schema-free LLM, canonicalized LLM, schema-guided LLM, validator/repair, hybrid enrichment | schema validity, structural acceptance, precision/recall/F1, provenance | formal scoring and prediction validation reports |
| Agentic validation | pre-loop, validator, refiner, critic, post-loop | violation reduction, repair/rejection, unsupported relation rate | agentic diagnostic reports |
| KG-RAG grounding | vector-only, graph, and routed KG-RAG | answer correctness, citation precision/recall, unsupported claim rate | retrieval and LLM answer-generation reports |
| Autonomous failure boundary | automated diagnostics, quarantine, adjudication, independent audit | failure categories, profile/gold-boundary cases, abstention status | reviewer-defense and adjudication reports |

## research question-To-Evidence Map

| research question | Safe claim | Evidence status |
|---|---|---|
| Schema-constrained extraction | Schema constraints improve the validity and auditability of accepted advisory-event facts. | Strong for current source-bounded artifacts. |
| Agentic validation | The agentic loop provides auditable repair and rejection behavior. | Moderate; useful as diagnostics, not autonomous ontology construction. |
| KG-RAG grounding | KG-RAG improves selected source-bounded grounding diagnostics against vector-only answers. | Moderate-strong for the current matched comparison; not universal GraphRAG superiority. |
| Autonomous failure boundary | Remaining errors are categorized and runtime gates are explicit. | Moderate; automated diagnostics exist, external expert certification does not. |

## Result Numbers To Reuse Carefully

Use the concise dashboard as the source of current headline numbers:

- `reports/stages/nasa_atmonto_s7_retrieval.md`

Current headline results:

- KG provenance completeness: 1.0
- KG evidence-in-source rate: 1.0
- valid triples: 448
- KG-RAG correctness: 0.9667
- KG-RAG citation precision: 1.0
- KG-RAG citation recall: 0.6084
- KG-RAG unsupported claim rate: 0.0167
- matched vector-only correctness: 0.5
- matched vector-only unsupported claim rate: 0.5
- human-review candidates: 9
- profile/gold-boundary failures: 3

## Claim Boundary

Safe:

- Bounded schema-constrained Agentic KG-RAG prototype.
- Retrospective FAA ATCSCC advisories.
- Source-bounded evidence spans and provenance.
- Layered metrics instead of a single overall score.
- Automated diagnostics with explicit human-review boundary.

Unsafe:

- Complete aviation ontology.
- NASA ATMONTO as full ground truth.
- Universal GraphRAG superiority.
- Automated agents replacing human review.
- Live operational ATC decision support.
- Externally certified aviation benchmark.

## Chapter Skeleton

1. Introduction
   - ATCSCC advisories as semi-structured event records.
   - Need for evidence-grounded extraction and answer support.
   - Bounded contribution and non-operational claim boundary.
2. Related Work
   - Schema-guided extraction and KG construction.
   - KG quality evaluation.
   - GraphRAG and citation-faithful QA.
   - Aviation LLM / ATM information systems.
3. Method
   - Source snapshot.
   - Schema/profile.
   - Extraction systems.
   - Agentic validation/refinement.
   - Event graph and KG-RAG.
4. Experiments
   - Schema-constrained extraction.
   - Agentic validation and ambiguity alignment.
   - Retrieval and answer generation.
   - Autonomous failure and audit boundary.
5. Results
   - Layered table, no mixed overall score.
   - research question-by-research question interpretation.
6. Discussion
   - Why schema and evidence boundaries matter.
   - Where graph evidence helps.
   - Failure taxonomy.
7. Limitations
   - Retrospective source family.
   - No live ATC support.
   - No external expert certification.
   - No domain-general proof.
8. Conclusion
   - Master-project contribution and future work.

## Future Work Boundary

Future work may mention:

- More ATCSCC source dates.
- Separate profiles for new source families.
- Human/expert review.
- Better visual demo.
- Domain transfer beyond aviation.

These should not become new core tasks for the current master project.
