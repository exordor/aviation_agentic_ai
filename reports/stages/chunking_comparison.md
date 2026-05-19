# Chunking Comparison

- Run ID: `chunking-comparison-20260519T004847Z`
- Questions: 10
- Vector top k: 5
- Target chars: 1200
- Overlap chars: 150
- Rebuild chunks: True
- Rebuild indexes: True

## Ranking

| Rank | Strategy | Recall@5 | MRR@5 | Context Precision@5 |
| ---: | --- | ---: | ---: | ---: |
| 1 | structure_aware | 1.0 | 0.82 | 0.52 |
| 2 | sentence_recursive | 1.0 | 0.7917 | 0.46 |
| 3 | fixed_window | 1.0 | 0.7583 | 0.42 |
| 4 | semantic_meta_like | 0.9 | 0.7333 | 0.5 |

## Strategy Details

| Strategy | Chunks | Avg chars | P95 chars | Boundary preservation | Tradeoff | Recommendation |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| fixed_window | 35 | 1034.11 | 1196 | 0.3714 | Controllable baseline, but it can cut through semantic boundaries. | Use as a stable baseline and regression check. |
| sentence_recursive | 35 | 1022.11 | 1191 | 0.2571 | Reduces mid-sentence cuts while keeping chunk sizes predictable. | Use when sentence integrity matters more than strict size regularity. |
| structure_aware | 267 | 233.36 | 1080 | 1.0 | Better preserves handbook section and list boundaries. | Prefer for handbook chapters with headings, lists, and page-local sections. |
| semantic_meta_like | 56 | 580.55 | 712 | 1.0 | Approximates semantic boundary detection; more context-aware but less deterministic than rule-only strategies. | Use for exploratory retrieval runs where semantic boundary quality is worth extra complexity. |

## Strategy Explanations

### fixed_window

Controllable baseline, but it can cut through semantic boundaries. It ties for the best source-page Recall@5 in this run.

- Retrieval: Recall@5=1.0, MRR@5=0.7583, Context Precision@5=0.42
- Recommendation: Use as a stable baseline and regression check.

### sentence_recursive

Reduces mid-sentence cuts while keeping chunk sizes predictable. It ties for the best source-page Recall@5 in this run.

- Retrieval: Recall@5=1.0, MRR@5=0.7917, Context Precision@5=0.46
- Recommendation: Use when sentence integrity matters more than strict size regularity.

### structure_aware

Better preserves handbook section and list boundaries. It ties for the best source-page Recall@5 in this run. It places relevant evidence near the top of the result list. High boundary preservation indicates fewer semantic or structural cuts.

- Retrieval: Recall@5=1.0, MRR@5=0.82, Context Precision@5=0.52
- Recommendation: Prefer for handbook chapters with headings, lists, and page-local sections.

### semantic_meta_like

Approximates semantic boundary detection; more context-aware but less deterministic than rule-only strategies. High boundary preservation indicates fewer semantic or structural cuts.

- Retrieval: Recall@5=0.9, MRR@5=0.7333, Context Precision@5=0.5
- Recommendation: Use for exploratory retrieval runs where semantic boundary quality is worth extra complexity.

