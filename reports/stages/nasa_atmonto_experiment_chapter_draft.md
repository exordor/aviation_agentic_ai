# Schema-constrained Agentic KG-RAG for evidence-grounded FAA ATCSCC advisory question answering

## Claim Boundary

The experiment is retrospective and source-bounded. NASA ATMONTO-derived terms are used as a lightweight application schema, not as a complete aviation ontology or ground truth. The thesis evaluates schema-constrained event extraction, agentic validation/refinement, KG-RAG grounding, and failure/human-review boundaries as separate layers; it does not make live operational ATC decision-support claims.

## Research Questions

- RQ1: Can schema-constrained LLM extraction produce valid and evidence-linked event records from ATCSCC advisories?
- RQ2: Does an agentic validation-refinement loop reduce schema violations and unsupported relations?
- RQ3: Does KG-RAG improve evidence grounding and citation quality compared with vector-only RAG?
- RQ4: What failure types remain, and where does human review remain necessary?

## Schema Role

The ATCSCC profile is an application schema for bounded advisory-event extraction. It constrains accepted fields, relation names, evidence spans, and validation checks, but it is not evaluated as a complete aviation ontology.

## Experiment A: Schema-constrained advisory event extraction

Compare rule-only, schema-slice LLM, validator-repair, and hybrid S4 outputs against reviewed ATCSCC advisory facts, keeping structural schema validity, evidence support, and semantic scores separate.

## Experiment B: Agentic validation and CQ queryability

Use validator/refiner/critic artifacts plus CQ query templates to measure whether graph outputs recover source-bounded answer sets with evidence and fewer unsupported relations.

## Experiment C: KG-RAG grounding and answer generation

Generate deterministic source-only, vector proxy, graph-only, and hybrid GraphRAG answers over the answer-eval benchmark with a critic gate before S4 evidence enters graph/hybrid answers. Report citation, faithfulness, unsupported-claim, and abstention metrics separately.

- Hybrid answer correctness: 0.9444
- Hybrid evidence faithfulness: 0.9444
- S7 deterministic routed live lexical KG-RAG correctness: 0.6435 under the stricter timestamp-preserving answer-value scorer.
- S7 fixed-budget LLM v3 live lexical route correctness: 0.9667 on 30 selected cases; source-local guarded dense route correctness: 0.9333 on 30 selected cases.
- S7 graph-health diagnostic: routed KG-RAG uses graph context in 39.75% of cases, preserves target-source hit rate at 1.0, and reaches answer-set F1 0.9833 while avoiding graph context for abstention/time-window templates.
- S7 source-local dense guard: deterministic S7 dense routed answer correctness increased from 0.3344 to 0.6215, with target-source hit rate increasing from 0.4069 to 0.9685 and guard rate 0.5615. This should be interpreted as metadata/source-bounded guarded dense retrieval, not pure dense embedding superiority.
- S7 LLM failure review: previous dense source-miss, wrong-context abstention, controlled-element metadata leakage, and compound route-semantics partial-answer failures were addressed; the remaining 3 failures are cause-condition over-answer/profile-boundary cases.
- S7 route-semantics partial-answer ablation: on the four selected route-semantics cases, both routed live lexical and guarded dense modes reached strict correctness 1.0, partial contract satisfaction 1.0, value F1 1.0, abstain rate 0.0, and unsupported rate 0.0 when prompted to return supported fields and list missing `reRouteType` / `reRouteReason` separately; this motivated the targeted v3 primary prompt.
- S7 human-review candidate package, adjudication, and profile decision: 9 generated-answer cases were packaged for review, including all 3 current failures and 6 coverage-success examples. Deterministic adjudication classifies the 3 failures as profile/gold-boundary cases and leaves strict S7 metrics unchanged. The profile-decision what-if shows that a predicate whitelist would correct those 3 selected records, but it does not replace strict metrics or change gold/profile artifacts. This is a review queue and project-level adjudication, not reviewed evidence.
- Boundary: S7 LLM results include deterministic JSON/schema repair for abstention and ATCSCC time-window normalization. They are diagnostic and source-bounded, not human review or operational ATC certification.

## Experiment D: Failure analysis and human-review boundary

Classify remaining extraction, retrieval, profile/gold-boundary, and answer-overreach failures, and keep automated diagnostics separate from human or expert review.
