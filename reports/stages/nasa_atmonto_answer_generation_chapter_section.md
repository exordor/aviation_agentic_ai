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

## Experiment D: Failure analysis and human-review boundary

Classify remaining extraction, retrieval, profile/gold-boundary, and answer-overreach failures, and keep automated diagnostics separate from human or expert review.
