# ATMONTO Advisory KG and GraphRAG Experiment Chapter Draft

## Claim Boundary

The experiment is retrospective and source-bounded. It evaluates extraction, CQ queryability, and generated-answer behavior as separate layers; it does not make live operational decision-support claims.

## Experiment A: ATMONTO-constrained KG extraction

Compare rule-only, schema-slice LLM, validator-repair, and hybrid S4 outputs against reviewed ATCSCC advisory facts.

## Experiment B: CQ queryability / answer-set quality

Use six CQ query templates to measure whether graph outputs recover source-bounded answer sets with evidence.

## Experiment C: GraphRAG answer generation

Generate deterministic source-only, vector proxy, graph-only, and hybrid GraphRAG answers over the answer-eval benchmark with a critic gate before S4 evidence enters graph/hybrid answers. Extend this with S7 retrieval/answer-generation controls and a bounded LLM answer-generation check over routed token-matched live lexical and dense GraphRAG contexts.

- Hybrid answer correctness: 0.8333
- Hybrid evidence faithfulness: 0.8333
- S7 deterministic routed live lexical GraphRAG correctness: 0.6435 under the stricter timestamp-preserving answer-value scorer.
- S7 fixed-budget LLM live lexical route correctness: 1.0 on 12 selected cases; dense route correctness: 0.5 on 12 selected cases.
- S7 graph-health diagnostic: routed GraphRAG uses graph context in 39.75% of cases, preserves target-source hit rate at 1.0, and reaches answer-set F1 0.9833 while avoiding graph context for abstention/time-window templates.
- Boundary: S7 LLM results include deterministic JSON/schema repair for abstention and ATCSCC time-window normalization. They are diagnostic and source-bounded, not human review or operational ATC certification.
