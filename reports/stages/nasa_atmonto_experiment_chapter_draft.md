# ATMONTO Advisory KG and GraphRAG Experiment Chapter Draft

## Claim Boundary

The experiment is retrospective and source-bounded. It evaluates extraction, CQ queryability, and generated-answer behavior as separate layers; it does not make live operational decision-support claims.

## Experiment A: ATMONTO-constrained KG extraction

Compare rule-only, schema-slice LLM, validator-repair, and hybrid S4 outputs against reviewed ATCSCC advisory facts.

## Experiment B: CQ queryability / answer-set quality

Use six CQ query templates to measure whether graph outputs recover source-bounded answer sets with evidence.

## Experiment C: GraphRAG answer generation

Generate deterministic source-only, vector proxy, graph-only, and hybrid GraphRAG answers over the answer-eval benchmark with a critic gate before S4 evidence enters graph/hybrid answers.

- Hybrid answer correctness: 0.8333
- Hybrid evidence faithfulness: 0.8333
