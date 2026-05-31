# PDF Backend Chunking Comparison

Structure quality and retrieval quality are reported separately. No universal PDF backend superiority claim is made.

Recommended default backend: `hybrid_docling_pymupdf` (candidate_default_not_final).

| Strategy | Backend | Chunks | Recall@5 | MRR@5 | Context Recall | Repairs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `fixed_large_baseline` | `pymupdf_fixed_large` | 27 | 0.99 | 0.8153 | 0.975 | 0 |
| `legacy_pymupdf_structure_aware_large` | `pymupdf_text_legacy` | 27 | 0.99 | 0.8153 | 0.975 | 0 |
| `recursive_medium_baseline` | `pymupdf_recursive_medium` | 48 | 0.94 | 0.7733 | 0.945 | 0 |
| `docling_structure_aware_large` | `docling_structure` | 36 | 0.77 | 0.6783 | 0.755 | 0 |
| `hybrid_docling_pymupdf_structure_aware_large` | `hybrid_docling_pymupdf` | 36 | 0.77 | 0.6783 | 0.755 | 14 |

## Interpretation

- Legacy PyMuPDF structure-aware chunks are a baseline for comparability.
- Docling and hybrid chunks use Docling labels rather than PyMuPDF heading heuristics.
- Hybrid repairs are counted separately from retrieval metrics.
- Insufficient-evidence labels are excluded from supported-answer retrieval aggregates.
