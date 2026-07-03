# PDF Extraction Comparison

Docling is treated as structure authority for this document; PyMuPDF heuristic headings are legacy baseline only. No human/expert review is claimed.

| Backend | Precision | Recall | F1 | False headings | Runtime s | Artifacts | Repairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pymupdf_text_legacy` | 0.0887 | 0.9167 | 0.1617 | 113 | 0.4057 | 0 | 0 |
| `pymupdf_text_sort` | 0.1071 | 0.25 | 0.15 | 25 | 0.4057 | 0 | 0 |
| `pymupdf_blocks` | 0.0968 | 0.25 | 0.1396 | 28 | 0.4057 | 0 | 0 |
| `docling_structure` | 0.8 | 1.0 | 0.8889 | 3 | 13.5591 | 3 | 0 |
| `hybrid_docling_pymupdf` | 0.8 | 1.0 | 0.8889 | 3 | 13.9648 | 38 | 14 |

## Interpretation

- PyMuPDF plain-text heading heuristics are retained only as a legacy baseline.
- Docling labels provide the structural authority for section/table/list boundaries.
- The hybrid backend uses PyMuPDF to detect and conservatively repair Docling text artifacts.
- Downstream retrieval claims require the separate PDF backend chunking comparison.
