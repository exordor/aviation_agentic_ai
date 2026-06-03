# ATCSCC S7 Graph-Use Gate Plan

Date: 2026-06-03

Status: S7 deterministic proxies implemented for answer generation,
CQ queryability, and retrieval-only graph-use evaluation. True live vector-index
retrieval and tokenizer-backed token matching remain planned extensions.

## Purpose

The S7 graph-use gate answers a narrow SOTA question:

> For ATCSCC advisory questions, when should the system use graph context,
> vector/source context, or a hybrid of both?

This is required because the literature does not support a blanket claim that
GraphRAG is always better than vector RAG. The gate makes graph use a
query-level decision.

## Current Implementation

The current implementation has three deterministic layers:

- answer-generation proxy: `reports/stages/nasa_atmonto_answer_generation.md`
- CQ answer-set queryability proxy: `reports/stages/nasa_atmonto_cq_query_evaluation.md`
- retrieval-only graph-use proxy: `reports/stages/nasa_atmonto_s7_retrieval.md`

The core retrieval implementation is in
`src/aviation_agentic_ai/reporting/nasa_atmonto_s7_retrieval.py`.

Two new answer modes are now reported:

| Mode | Purpose | Current status |
| --- | --- | --- |
| `token_matched_vector_rag` | Vector/source-text control with the hybrid context budget recorded as target. | Implemented as deterministic proxy; no live vector index rerun. |
| `routed_graphrag` | Uses the graph-use gate to choose vector/source or hybrid graph context by CQ template. | Implemented as deterministic proxy over the 18-label answer benchmark. |

The current gate is intentionally conservative. It does not claim live retriever
performance; it evaluates whether the routing policy improves or preserves
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

| Mode | Answer F1 | Abstention correct | Path support | Avg tokens | Token target |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_oracle` | 1.0 | 1.0 | n/a | 7.65 | n/a |
| `vector_rag_proxy` | 1.0 | 1.0 | n/a | 7.65 | n/a |
| `token_matched_vector_proxy` | 1.0 | 1.0 | n/a | 7.65 | 14.88 |
| `graph_only` | 0.5248 | 0.01 | 1.0 | 9.32 | n/a |
| `hybrid_graphrag` | 0.5248 | 0.01 | 1.0 | 14.88 | n/a |
| `routed_graphrag` | 0.9885 | 1.0 | 1.0 | 9.9 | n/a |

Interpretation:

- the routed gate avoids the main graph-only failure mode: returning graph facts
  for missing-field/abstention questions;
- graph path support is available for graph-worthy questions, but this does not
  imply that graph-only retrieval is safe for all templates;
- the token-matched vector proxy records the hybrid token target without using
  graph triples, giving the next live retrieval run a fair control target.

## What This Proves

This proves that the project now has an explicit graph-use gate, a retrieval-only
route evaluation, graph path-support reporting, and a token-budget control field.
It also produces a negative/qualified result: graph context is not automatically
better in the current scaffold.

At the CQ answer-set layer, it proves that the gate can be evaluated over the
existing queryability benchmark and preserves the current best S4 aggregate.

## What This Does Not Prove

This does not yet prove:

- real vector retrieval performance over a live ATCSCC text index;
- real graph traversal retrieval performance over a materialized ATCSCC KG;
- token-matched retrieval with actual model tokenizer counts;
- graph superiority on natural-language ATCSCC questions.

## Next Implementation Step

The next SOTA upgrade is a live retrieval S7 run:

1. materialize a live ATCSCC text index and graph traversal layer;
2. rerun vector-only, graph-only, hybrid, routed, and token-matched vector
   retrieval over the same query set;
3. replace whitespace token estimates with tokenizer-backed counts and add
   latency;
4. only then re-run natural-language answer generation on the routed retrieval
   outputs.
