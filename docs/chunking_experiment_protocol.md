# Chunking Experiment Protocol

## Purpose

Chunking controls the evidence units indexed by vector retrieval and later used
by GraphRAG. A chunking strategy can change whether the retriever returns the
right evidence span, whether the returned context is too narrow or too broad,
how many chunks must be embedded, and how much downstream KG extraction would
cost. The project therefore reports chunking as a retrieval-design experiment,
not as a single global winner.

The original `reports/stages/chunking_comparison.json` and `.md` report is a
10-question pilot over boundary CQs. It is useful for regression checks and
historical comparison, but it is too small for the main thesis retrieval claim.
The benchmark-v2 report uses `data/cqs/06_phak_ch4_0.benchmark_v2.gold.json`
with 120 labels and keeps supported labels separate from insufficient-evidence
labels.

## Chunking Families

Mainstream RAG and GraphRAG systems commonly use several chunking families:

- Fixed-size sliding window chunking.
- Recursive sentence or paragraph chunking.
- Structure-aware heading, page, section, and list chunking.
- Embedding-based semantic chunking.
- Proposition or atomic-claim chunking.
- Hierarchical parent-child chunking.
- Contextual retrieval with deterministic or generated context prefixes.
- Late chunking, where embeddings are produced before final chunk pooling.

This repository currently implements fixed-window, sentence-recursive,
structure-aware, lexical semantic-meta-like, fixed size tiers, recursive size
tiers, embedding semantic chunking with lexical fallback, deterministic
proposition-like chunking, hierarchical parent-child chunk scaffolding, and
deterministic contextual prefixes. Late chunking remains future work and is not
exposed as a runnable strategy.

## Metrics

The benchmark-v2 chunking report uses layered metrics and no single overall
score. Retrieval metrics are primary only for supported labels:

- Recall@5 and Recall@10.
- Precision@5.
- MRR@5 and MRR@10.
- NDCG@10.
- Context Precision@5.
- Context Recall.
- Bootstrap 95% confidence intervals for Recall@5, Recall@10, MRR@5,
  NDCG@10, and Context Recall.

Chunking and cost diagnostics are reported beside retrieval metrics:

- Chunk count.
- Average chunk size.
- P95 chunk size.
- Average whitespace-token count.
- Overlap redundancy.
- Boundary preservation.
- Index build time.
- Query latency mean and p95.
- Index size when available.
- KG extraction cost impact notes inferred from chunk count and chunk size.

Insufficient-evidence labels have no gold retrieval target. The report therefore
does not treat them as ordinary recall failures. It reports whether top-5
retrieved context overlaps key entities, because such context may look
misleading even when the correct answer should be abstention.

## Interpretation Rules

The benchmark-v2 report may rank strategies by supported-only retrieval metrics
for readability, but that ranking is benchmark-specific. The thesis should not
claim that one chunker is universally best. Small chunks may localize facts
better, large chunks may preserve broader context, and aviation questions about
definitions, causal relations, and cross-page evidence can prefer different
chunk sizes.

`embedding_semantic` is real embedding-based semantic chunking only when the
configured sentence-transformers model loads successfully. If model loading
fails, the report records `semantic_backend=fallback_lexical`.

`proposition_like` is deterministic proposition-ish segmentation based on
sentence cues. It is not LLM proposition extraction.

`hierarchical_parent_child` creates child chunks with parent metadata. The
current benchmark-v2 retrieval indexes child text and records parent context as
metadata, so parent-return retrieval is marked as partial.
