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
- S7 fixed-budget LLM v3 live lexical route correctness: 0.9667 on 30 selected cases; source-local guarded dense route correctness: 0.9333 on 30 selected cases.
- S7 graph-health diagnostic: routed GraphRAG uses graph context in 39.75% of cases, preserves target-source hit rate at 1.0, and reaches answer-set F1 0.9833 while avoiding graph context for abstention/time-window templates.
- S7 source-local dense guard: deterministic S7 dense routed answer correctness increased from 0.3344 to 0.6215, with target-source hit rate increasing from 0.4069 to 0.9685 and guard rate 0.5615. This should be interpreted as metadata/source-bounded guarded dense retrieval, not pure dense embedding superiority.
- S7 LLM failure review: previous dense source-miss, wrong-context abstention, controlled-element metadata leakage, and compound route-semantics partial-answer failures were addressed; the remaining 3 failures are cause-condition over-answer/profile-boundary cases.
- S7 route-semantics partial-answer ablation: on the four selected route-semantics cases, both routed live lexical and guarded dense modes reached strict correctness 1.0, partial contract satisfaction 1.0, value F1 1.0, abstain rate 0.0, and unsupported rate 0.0 when prompted to return supported fields and list missing `reRouteType` / `reRouteReason` separately; this motivated the targeted v3 primary prompt.
- S7 human-review candidate package and adjudication: 9 generated-answer cases were packaged for review, including all 3 current failures and 6 coverage-success examples. Deterministic adjudication classifies the 3 failures as profile/gold-boundary cases and leaves strict S7 metrics unchanged. This is a review queue and project-level adjudication, not reviewed evidence.
- Boundary: S7 LLM results include deterministic JSON/schema repair for abstention and ATCSCC time-window normalization. They are diagnostic and source-bounded, not human review or operational ATC certification.
