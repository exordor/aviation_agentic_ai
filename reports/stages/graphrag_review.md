# GraphRAG Review

## Summary

GraphRAG's current value is KG evidence coverage and explainable structured evidence, not higher page-level Recall@5 than vector-only retrieval.

## Fixed-Window Baseline

| Mode | Recall@5 | MRR@5 | Context Precision@5 | KG evidence coverage | Citation completeness |
| --- | ---: | ---: | ---: | ---: | ---: |
| vector | 1.0 | 0.7583 | 0.42 | 0.0 | 1.0 |
| graph | 0.8 | 0.65 | 0.49 | 0.9 | 1.0 |
| hybrid | 0.9 | 0.7533 | 0.4 | 0.9 | 1.0 |

Hybrid lift:
- vs vector Recall@5: -0.1
- vs graph Recall@5: 0.1

## Chunking Interpretation

- Best chunking strategy: `structure_aware`.
- `structure_aware` preserves handbook section/list boundaries, which explains its stronger MRR and Context Precision in the chunking comparison.

## Failure Cases

- `06-phak-ch4-0-p05-986bfc7e8f`: page_recall_miss_but_kg_evidence_found (source page 5).
- `06-phak-ch4-0-p08-84dd3b3d9f`: retrieval_hit_but_kg_evidence_missing (source page 8).

## Structure-Aware Experiment

| Mode | Recall@5 | MRR@5 | Context Precision@5 | KG evidence coverage | Citation completeness |
| --- | ---: | ---: | ---: | ---: | ---: |
| vector | 1.0 | 0.82 | 0.52 | 0.0 | 1.0 |
| graph | 0.9 | 0.7033 | 0.56 | 0.9 | 1.0 |
| hybrid | 1.0 | 0.7367 | 0.52 | 0.9 | 1.0 |

## Interpretations

- GraphRAG value is evidence structure, not current page-level Recall lift.
  Evidence: Fixed-window vector Recall@5=1.0; hybrid Recall@5=0.9; graph/hybrid KG evidence coverage=0.9/0.9.
  Implication: Do not claim Hybrid RAG beats vector-only retrieval on the current coarse page-level benchmark.
- Vector-only can win page-level Recall@5 because the gold label is coarse.
  Evidence: The current gold target is source_page, so any chunk from the right page counts even when it lacks structured relations.
  Implication: Add chunk/span-level gold labels before drawing stronger GraphRAG conclusions.
- Hybrid fusion can lower page Recall when graph results add related but off-page evidence.
  Evidence: Fixed-window hybrid lift vs vector Recall@5=-0.1.
  Implication: Review fusion failures before tuning graph weight or hop depth.
- structure_aware is the best chunking candidate for the next KG.
  Evidence: Chunking comparison ranked it first by Recall@5/MRR@5/Context Precision@5.
  Implication: Re-extract KG on structure-aware chunks before using it as the Hybrid RAG default.
- Structure-aware Hybrid RAG is available as a second experiment.
  Evidence: Its metrics are recorded separately and should be compared with fixed-window.
  Implication: Use the paired reports to decide the default chunking strategy.

## Recommendations

- Report GraphRAG as adding structured KG evidence, not as current page Recall@5 winner.
- Use structure-aware chunks for the next KG extraction candidate.
- Refine gold labels to chunk/span-level evidence before optimizing fusion.
