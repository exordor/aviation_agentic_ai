# ATCSCC S7 Graph-Use Gate Plan

Date: 2026-06-03

Status: S7 deterministic proxies implemented for answer generation and CQ
queryability, plus a small fixed-budget LLM answer-generation check over frozen
S7 contexts. Retrieval-only S7 now includes live TF-IDF lexical-vector
retrieval, materialized ATCSCC fact-graph traversal, tokenizer-backed
token-matched controls, dense embedding retrieval, and latency reporting. The
S7 answer-generation rerun evaluates deterministic answers over routed live
lexical and dense retrieval contexts, and the LLM check tests the same routed
token-matched live/dense contexts on a bounded sample.

## Purpose

The S7 graph-use gate answers a narrow SOTA question:

> For ATCSCC advisory questions, when should the system use graph context,
> vector/source context, or a hybrid of both?

This is required because the literature does not support a blanket claim that
GraphRAG is always better than vector RAG. The gate makes graph use a
query-level decision.

## Current Implementation

The current implementation has three deterministic layers and one bounded model
layer:

- answer-generation proxy: `reports/stages/nasa_atmonto_answer_generation.md`
- CQ answer-set queryability proxy: `reports/stages/nasa_atmonto_cq_query_evaluation.md`
- retrieval-only graph-use and live lexical/dense-vector report:
  `reports/stages/nasa_atmonto_s7_retrieval.md`
- S7 live-retrieval answer-generation report:
  `reports/stages/nasa_atmonto_s7_answer_generation.md`
- S7 fixed-budget LLM answer-generation report:
  `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`
- S7 graph-health by CQ group report:
  `reports/stages/nasa_atmonto_s7_graph_health.md`
- S7 LLM failure review:
  `reports/stages/nasa_atmonto_s7_llm_failure_review.md`

The core retrieval implementation is in
`src/aviation_agentic_ai/reporting/nasa_atmonto_s7_retrieval.py`.
The S7 answer-generation rerun is in
`src/aviation_agentic_ai/reporting/nasa_atmonto_s7_answer_generation.py`.
The fixed-budget S7 LLM check is in
`src/aviation_agentic_ai/reporting/nasa_atmonto_s7_llm_answer_generation.py`.
The graph-health CQ-group diagnostics are in
`src/aviation_agentic_ai/reporting/nasa_atmonto_s7_graph_health.py`.

Two new answer modes are now reported:

| Mode | Purpose | Current status |
| --- | --- | --- |
| `token_matched_vector_rag` | Vector/source-text control with the hybrid context budget recorded as target. | Implemented as deterministic answer-generation proxy; retrieval-only report now includes token-matched live lexical-vector control. |
| `routed_graphrag` | Uses the graph-use gate to choose vector/source or hybrid graph context by CQ template. | Implemented as deterministic proxy over the 18-label answer benchmark. |

The fixed-budget LLM check evaluates:

| Mode | Purpose | Current status |
| --- | --- | --- |
| `routed_token_matched_live_tfidf_graphrag` | Token-matched routed GraphRAG over live lexical source retrieval. | Evaluated on 12 selected cases, two per CQ template. |
| `routed_token_matched_dense_graphrag` | Token-matched routed GraphRAG over dense source retrieval. | Evaluated on 12 selected cases, two per CQ template. |

The current gate is intentionally conservative. The live retrieval layer now
includes both a lexical TF-IDF source index and a local dense embedding index
over frozen ATCSCC records. It evaluates whether routing improves or preserves
answer behavior inside the source-bounded scaffold.

## Route Policy

| Query template | Gate decision | Reason |
| --- | --- | --- |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `hybrid_graphrag` | Entity-role and affected-scope questions benefit from graph facts plus source spans. |
| `QT-Q01-TIME-WINDOW` | `vector_rag` | Direct temporal fields are source-local and do not require graph expansion. |
| `QT-Q01-CAUSE-CONDITION` | `hybrid_graphrag` | Cause/status fields need source text plus ontology-constrained facts. |
| `QT-Q01-STATUS-ACTION` | `hybrid_graphrag` | Lifecycle/action semantics can depend on TMI type and evidence context. |
| `QT-Q01-ROUTE-SEMANTICS` | `hybrid_graphrag` | Route questions are relation-heavy and graph-worthy. |
| `QT-A01-ABSTENTION-FIELDS` | `vector_rag` | Abstention should be driven by source support and missing-field checks, not graph inference. |

## Current Proxy Results

### Answer-Generation Proxy

From `reports/stages/nasa_atmonto_answer_generation.md`:

| Mode | Correctness | Citation recall | Evidence faithful | Unsupported claim rate | Avg context tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| `vector_rag` | 1.0 | 0.4167 | 1.0 | 0.0 | 5.11 |
| `token_matched_vector_rag` | 1.0 | 0.4167 | 1.0 | 0.0 | 5.11 actual, 14.06 target |
| `graph_only` | 0.8333 | 0.3333 | 0.8333 | 0.0833 | 48.78 |
| `hybrid_graphrag` | 0.8333 | 0.5833 | 0.8333 | 0.0833 | 14.06 |
| `routed_graphrag` | 0.8333 | 0.5417 | 0.8333 | 0.0833 | 12.39 |

Interpretation:

- graph-only is currently the weakest mode because accepted S4 graph facts can
  still contain unsupported extras even after the critic gate;
- hybrid improves citation recall versus graph-only but inherits the same
  unsupported-claim risk;
- routed GraphRAG reduces average context tokens relative to always-hybrid but
  does not yet improve correctness or unsupported-claim rate;
- token-matched vector/source control remains the strongest in this deterministic
  scaffold, which means the project should not claim GraphRAG superiority from
  this pilot.

### CQ Queryability Proxy

From `reports/stages/nasa_atmonto_cq_query_evaluation.md`:

| Template | Selected system | F1 | Reason |
| --- | --- | ---: | --- |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `S4_hybrid_backbone_enrichment` | 0.5714 | entity/role semantics need hybrid KG context |
| `QT-Q01-TIME-WINDOW` | `S0_rule_only` | 0.9796 | direct temporal field; graph expansion unnecessary |
| `QT-Q01-CAUSE-CONDITION` | `S4_hybrid_backbone_enrichment` | 0.7961 | condition semantics benefit from semantic enrichment |
| `QT-Q01-STATUS-ACTION` | `S4_hybrid_backbone_enrichment` | 0.5517 | lifecycle/status semantics need source plus KG facts |
| `QT-Q01-ROUTE-SEMANTICS` | `S4_hybrid_backbone_enrichment` | 0.5937 | route questions are relation-heavy |
| `QT-A01-ABSTENTION-FIELDS` | `S4_hybrid_backbone_enrichment` | 0.8145 | critic-gated hybrid facts expose missing/unsupported fields |

Aggregate routed queryability proxy: micro-F1 0.7751, micro precision 0.7402,
micro recall 0.8135.

This equals the S4 aggregate in the current run because the only deterministic
override, time-window extraction, already matches S4. The result is still useful:
it shows that query-level routing can be represented without degrading the
existing best answer-set score, but it does not yet show a queryability gain.

### Retrieval-Only Proxy

From `reports/stages/nasa_atmonto_s7_retrieval.md`:

| Mode | Target hit | Answer F1 | Abstention correct | Path support | Avg context tokens | Token target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_oracle` | 1.0 | 1.0 | 1.0 | n/a | 19.78 | n/a |
| `vector_rag_proxy` | 1.0 | 1.0 | 1.0 | n/a | 19.78 | n/a |
| `token_matched_vector_proxy` | 1.0 | 1.0 | 1.0 | n/a | 19.78 | 38.96 |
| `live_tfidf_vector` | 1.0 | 0.8235 | 1.0 | n/a | 2001.44 | n/a |
| `token_matched_live_tfidf_vector` | 1.0 | 0.8235 | 1.0 | n/a | 38.96 | 38.96 |
| `dense_embedding_vector` | 0.0473 | 0.0729 | 0.09 | n/a | 1327.38 | n/a |
| `token_matched_dense_embedding_vector` | 0.0095 | 0.0385 | 0.02 | n/a | 38.96 | 38.96 |
| `graph_only` | 0.9968 | 0.5205 | 0.01 | 1.0 | 25.18 | n/a |
| `hybrid_graphrag` | 1.0 | 0.5205 | 0.01 | 1.0 | 38.96 | n/a |
| `routed_graphrag` | 1.0 | 0.9833 | 1.0 | 1.0 | 24.82 | n/a |
| `routed_live_tfidf_graphrag` | 1.0 | 0.8534 | 1.0 | 1.0 | 1326.48 | n/a |
| `routed_token_matched_live_tfidf_graphrag` | 1.0 | 0.8534 | 1.0 | 1.0 | 38.96 | 38.96 |
| `routed_dense_graphrag` | 0.4385 | 0.2229 | 0.09 | 1.0 | 783.56 | n/a |
| `routed_token_matched_dense_graphrag` | 0.4069 | 0.1933 | 0.02 | 1.0 | 38.96 | 38.96 |

Interpretation:

- the routed gate avoids the main graph-only failure mode: returning graph facts
  for missing-field/abstention questions;
- graph path support is available for graph-worthy questions, but this does not
  imply that graph-only retrieval is safe for all templates;
- live lexical-vector retrieval can locate the source records in this
  source-bounded setup, but it uses much larger contexts unless token-matched;
- the token-matched live lexical-vector control matches the hybrid context
  budget exactly and keeps graph triples disabled;
- the graph modes now traverse a materialized source-predicate-fact graph with
  100 source nodes, 666 fact nodes, and 1332 edges;
- dense embedding retrieval is a negative result in this benchmark because the
  CQs are source-bounded and generic; without explicit metadata filtering, dense
  semantic similarity often retrieves plausible but wrong advisories.

### S7 Live-Retrieval Answer-Generation Rerun

From `reports/stages/nasa_atmonto_s7_answer_generation.md`:

| Mode | Correctness | Citation recall | Evidence faithful | Unsupported claim rate | Abstention correct | Avg context tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_oracle` | 1.0 | 0.3423 | 1.0 | 0.0 | 1.0 | 19.78 |
| `hybrid_graphrag` | 0.9306 | 0.4611 | 0.9306 | 0.0347 | 1.0 | 38.96 |
| `routed_graphrag` | 0.9306 | 0.4133 | 0.9306 | 0.0347 | 1.0 | 24.82 |
| `token_matched_live_tfidf_vector` | 0.5426 | 0.4564 | 0.5426 | 0.2435 | 1.0 | 38.96 |
| `routed_token_matched_live_tfidf_graphrag` | 0.6435 | 0.4611 | 0.6435 | 0.1828 | 1.0 | 38.96 |
| `token_matched_dense_embedding_vector` | 0.0252 | 0.2166 | 0.0315 | 0.6546 | 0.4385 | 38.96 |
| `routed_token_matched_dense_graphrag` | 0.3344 | 0.4138 | 0.3344 | 0.317 | 0.6909 | 38.96 |

Interpretation:

- after preserving ISO timestamp values during answer-value normalization, this
  rerun is stricter than the earlier table that collapsed time values such as
  `2026-05-19T13:22:00Z` to `00Z`;
- routed live lexical GraphRAG no longer preserves always-hybrid correctness
  under the token-matched budget, but still improves over token-matched lexical
  vector-only retrieval on this stricter answer-generation metric;
- always-live lexical retrieval is weaker than routed GraphRAG for some
  graph-worthy templates, while source-oracle and always-hybrid remain important
  upper/control bounds;
- dense retrieval remains a negative/qualified result for direct source-bounded
  advisory questions, especially abstention and entity/route templates.

### S7 Graph Health by CQ Group

From `reports/stages/nasa_atmonto_s7_graph_health.md`:

| Mode | Cases | Graph-context rate | Path support | Answer F1 | Abstention correct | Target hit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `graph_only` | 317 | 0.9968 | 1.0 | 0.5205 | 0.01 | 0.9968 |
| `hybrid_graphrag` | 317 | 0.9968 | 1.0 | 0.5205 | 0.01 | 1.0 |
| `routed_graphrag` | 317 | 0.3975 | 1.0 | 0.9833 | 1.0 | 1.0 |
| `routed_token_matched_live_tfidf_graphrag` | 317 | 0.3975 | 1.0 | 0.8534 | 1.0 | 1.0 |
| `routed_token_matched_dense_graphrag` | 317 | 0.3975 | 1.0 | 0.1933 | 0.02 | 0.4069 |

Interpretation:

- graph context is available for graph-worthy CQ templates, but routing avoids
  graph context for time-window and abstention templates where source evidence
  is the safer context;
- `graph_only` and always-hybrid modes have high graph availability but fail
  expected abstention cases, which explains their low aggregate answer F1;
- routed graph use is therefore a query-policy result, not a claim that more
  graph context is always better.

### Fixed-Budget LLM Answer-Generation Check

From `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`:

| Mode | Selected | Answered | Correctness | Citation recall | Evidence faithful | Unsupported claim rate | Abstention correct | Avg context tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 12 | 12 | 1.0 | 0.6111 | 1.0 | 0.0 | 1.0 | 28.25 |
| `routed_token_matched_dense_graphrag` | 12 | 12 | 0.5 | 0.6111 | 0.5 | 0.3333 | 0.5 | 28.25 |

Interpretation:

- the small LLM run is useful as a SOTA-facing sanity check because it replaces
  deterministic answer strings with model-generated answers over frozen
  retrieved contexts and reports two cases per CQ template for each routed mode;
- the sample is deliberately bounded, so it supports cautious comparison and
  error discovery, not expert certification;
- the live lexical route answers all selected cases correctly after deterministic
  schema/time-window repair, while the dense route remains a negative result
  with failures concentrated in time-window, abstention, and route-semantics
  questions.

Manual failure review in
`reports/stages/nasa_atmonto_s7_llm_failure_review.md` classifies the dense
failures as:

- two dense source misses on source-local time-window CQs;
- two wrong-context abstentions where the scorer correctly requires target-source
  retrieval before abstention can count as correct;
- two compound route-semantics partial-answer failures where the evidence
  supports `controlledNASelement=BNA` but the LLM abstains because reroute
  type/reason are unsupported.

## What This Proves

This proves that the project now has an explicit graph-use gate, retrieval-only
route evaluation, live lexical-vector retrieval, dense retrieval, graph
path-support reporting, materialized graph traversal, tokenizer-backed
token-budget controls, latency reporting, deterministic generated-answer
evaluation over routed live retrieval contexts, graph-health diagnostics by CQ
group, and a 24-case fixed-budget LLM-generated answer check. It also produces two
negative/qualified results:
graph context is not automatically better in the current scaffold, and dense
retrieval is not automatically better than lexical/source-bounded retrieval for
generic ATCSCC CQs.

At the CQ answer-set layer, it proves that the gate can be evaluated over the
existing queryability benchmark and preserves the current best S4 aggregate.

## What This Does Not Prove

This does not yet prove:

- graph superiority with broad online LLM generation;
- human or domain-expert answer-quality certification;
- operational decision-support readiness for live ATCSCC use.

## Next Implementation Step

The next SOTA upgrade is to add deterministic dense-retrieval guards for
source-local CQs and refine the route-semantics CQ contract before expanding the
LLM sample beyond two cases per CQ template.
